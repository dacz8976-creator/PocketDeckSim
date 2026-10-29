#!/usr/bin/env python3
"""Draft (do NOT adopt) the engine candidate's adoption commit: main-d9d2e70 in rl/engine-2026-10-20/.

  adopt_draft.py VARS.json [--replace]

Builds ONE commit on top of VARS["base"] (the candidate branch tip) from a private index: nothing is checked out, the
working tree and refs/heads/main are never touched, nothing is pushed. The branch VARS["branch"] is set to it.
Files: rl/engine-2026-10-20/{deckgym,legality_scan,goldfish} (the candidate's tested blobs, mode 100755), SHA256SUMS,
README.md; project_manifest.json (available_release -> historical_releases with "superseded"; the new available_release;
latest_source_*); START_HERE.md, CLAUDE.md, rl/RUN5.md, rules/02, 05, 08, 09; make_predictions.py's CURRENT_ENGINE (its
deck-12 self-test keeps the Oct 12 value); test_journal.py's replay-B test under the Oct 12 value.
Values not known before Dustin's yes (the pin date, his words) are @@...@@ placeholders unless VARS gives them; re-run
this at adoption with them filled. Every edit replaces a text that must occur exactly once in the base file."""
import json, os, re, subprocess, sys, tempfile

REPO = '/home/dacz8976/pincand'
NEW_DIR = 'rl/engine-2026-10-20'
NAME = 'main-d9d2e70'
BUILT = 'd9d2e70458273b77c379a7424ad33a162289205a'
BUILT_TREE = '12e23abd9fe5cf720526dbcb2f6481d293aa5159'
OFFICIAL = 'c045ede0e6d69c9dcb8d4cb3165c8ada3f8ef72e'
BASE_MAIN = 'b829787c349316615f588553014e199497630a07'
CAND = 'rl/results/engine_candidate_2026-10-20'
PROGS = {  # name: (sha256, blob) -- the candidate's committed, tested programs
    'deckgym': ('245e11e8cf939da7ba12a50fbb18630c67b1fb2231a692dd0c259c4a01556745', '2d5c1673c324ddd9333b8974ce199ae6b870e768'),
    'legality_scan': ('bce5654bb51b8b8bc201fba353267c575c168291959c32de6ee1365ecf7db8e9', 'a0bfd36c69df934bd0a79a1492a3ffb3580d04d5'),
    'goldfish': ('f53e948997326174103d917642cde78edb788098a7e8a5faf702096c91390e35', '8b6739abb621ba3b578d7123ed439031b423f28a'),
}
SUMS_BLOB = '91d79afbc3ba446aaa819649508022272eca25f9'  # programs/SHA256SUMS: the three lines, deckgym, legality_scan, goldfish
OLD = dict(name='main-c045ede', dir='rl/engine-2026-10-12',
           deckgym='0a9199bca480acf6f862342e042b7f36bb885416659eafeef24485c1783158c4',
           legality_scan='bf9d75020558b843a4f71d80a848d9150daff44e34f3b2159c16539b015a0ec7',
           goldfish='d8cfb7799770e16623c5d5ddc47b3ce55a714d66ec541fa8eb476a77fcf79a84')


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
    replace = '--replace' in sys.argv
    base = gs('rev-parse', V['base'] + '^{commit}')
    branch = V.get('branch', 'laptop/engine-adoption-draft-2026-10-20')
    P = dict(
        PIN=V.get('pin_date') or '@@PIN_DATE@@',
        PIN_SHORT=V.get('pin_short') or '@@PIN_DATE_SHORT@@',
        APPROVED=V.get('approved') or "@@APPROVED: Dustin's words, verbatim, with the date@@",
        TC=V['tests_commit'][:8], TIP_TREE=gs('rev-parse', base + ':engine')[:8], SUITE=V['suite_count'],
        FLOOR_SHORT=V['floor_short'], FLOOR_LONG=V['floor_long'], SLOWPIN_RUN5=V['slowpin_run5'],
    )

    # ---- guards on the base -------------------------------------------------------------------------------------
    for a, b in ((BASE_MAIN, BUILT), (BUILT, base)):
        if subprocess.run(['git', '-C', REPO, 'merge-base', '--is-ancestor', a, b]).returncode:
            sys.exit(f'{a[:8]} is not an ancestor of {b[:8]}')
    if gs('rev-parse', 'origin/main') != BASE_MAIN:
        sys.exit('origin/main moved since b829787c: re-take the base texts (and consider a merge) before drafting')
    if gs('rev-parse', BUILT + ':engine') != BUILT_TREE:
        sys.exit('built tree mismatch')
    # the base's engine/ differs from the built tree only in test code: engine/tests/*, and hooks/core.rs below its first #[cfg(test)]
    changed = gs('diff', '--name-only', BUILT, base, '--', 'engine').splitlines()
    bad = [f for f in changed if not f.startswith('engine/tests/') and f != 'engine/src/hooks/core.rs']
    if bad:
        sys.exit(f'engine files other than tests changed since the built commit: {bad}')
    if 'engine/src/hooks/core.rs' in changed:
        a = git('show', f'{BUILT}:engine/src/hooks/core.rs').decode()
        b = git('show', f'{base}:engine/src/hooks/core.rs').decode()
        cut = a.index('#[cfg(test)]')
        if b.index('#[cfg(test)]') != cut or a[:cut] != b[:cut]:
            sys.exit('hooks/core.rs differs from the built commit before its first #[cfg(test)]')
    for d in ('engine/examples', 'engine/Cargo.toml', 'engine/Cargo.lock', 'engine/database.json', 'engine/src/players'):
        if gs('rev-parse', f'{BUILT}:{d}') != gs('rev-parse', f'{base}:{d}'):
            sys.exit(f'{d} differs from the built commit')
    if gs('rev-parse', f'{OFFICIAL}:engine/src/players') != gs('rev-parse', f'{base}:engine/src/players'):
        sys.exit('engine/src/players changed since main-c045ede')
    sw = lambda c: sorted(set(re.findall(r'DECKGYM_[A-Z0-9_]+', gs('grep', '-h', '-o', r'DECKGYM_[A-Z0-9_]*', c, '--', 'engine/src'))))
    if sw(BUILT) != sw(OFFICIAL):
        sys.exit('the built commit reads a different set of DECKGYM_* switches than main-c045ede')
    nsw = len(sw(BUILT))
    src_changed = gs('diff', '--name-only', OFFICIAL, BUILT, '--', 'engine/src').splitlines()
    for n, (sha, blob) in PROGS.items():
        line = gs('ls-tree', base, f'{CAND}/programs/{n}')
        if line != f'100755 blob {blob}\t{CAND}/programs/{n}':
            sys.exit(f'{n}: {line}')
    if gs('rev-parse', f'{base}:{CAND}/programs/SHA256SUMS') != SUMS_BLOB:
        sys.exit('programs/SHA256SUMS blob differs')
    sums = git('cat-file', 'blob', SUMS_BLOB).decode()
    if sums != ''.join(f'{PROGS[n][0]}  {n}\n' for n in ('deckgym', 'legality_scan', 'goldfish')):
        sys.exit('SHA256SUMS content')
    if gs('ls-tree', base, NEW_DIR):
        sys.exit(f'{NEW_DIR} exists in the base')

    show = lambda p: git('show', f'{base}:{p}').decode('utf-8')
    files = {}

    # ---- project_manifest.json ----------------------------------------------------------------------------------
    raw = show('project_manifest.json')
    m = json.loads(raw)
    if json.dumps(m, indent=2, ensure_ascii=False) + '\n' != raw:
        sys.exit('the manifest does not round-trip through json.dumps(indent=2)')
    old = m['available_release']
    want = dict(name=OLD['name'], artifact=OLD['dir'] + '/deckgym', sha256=OLD['deckgym'], legality_scan=OLD['dir'] + '/legality_scan',
                legality_scan_sha256=OLD['legality_scan'], goldfish=OLD['dir'] + '/goldfish', goldfish_sha256=OLD['goldfish'], source_commit=OFFICIAL)
    for k, v in want.items():
        if old.get(k) != v:
            sys.exit(f'manifest available_release.{k} is {old.get(k)!r}, not {v!r}')
    if any(r.get('name') == NAME for r in m['historical_releases']):
        sys.exit(f'{NAME} is already in the history')
    hist = dict(old)
    hist['superseded'] = (f"{P['PIN']} by {NAME} (the Growl-to-0 rule and upstream #385, #390, #401 Fossil part, #344 narrow; {NEW_DIR}/)")
    m['historical_releases'].append(hist)
    m['available_release'] = {
        'name': NAME,
        'artifact': f'{NEW_DIR}/deckgym', 'sha256': PROGS['deckgym'][0],
        'legality_scan': f'{NEW_DIR}/legality_scan', 'legality_scan_sha256': PROGS['legality_scan'][0],
        'goldfish': f'{NEW_DIR}/goldfish', 'goldfish_sha256': PROGS['goldfish'][0],
        'goldfish_note': old['goldfish_note'],
        'source_commit': BUILT,
        'source_working_tree': False,
        'built': (f"2026-10-20 (02:09-02:18 UTC) in WSL: cargo build --release --locked, --example legality_scan and --example goldfish, "
                  f"from one git archive of {BUILT} (branch laptop/engine-candidate-2026-10-20: main-c045ede's engine plus five engine "
                  f"commits; engine/ tree {BUILT_TREE[:8]}), in a fresh folder with an empty target directory, CARGO_BUILD_JOBS 2 "
                  f"({CAND}/RESULT.md, tests_and_builds.txt). source_commit is the built commit itself. main's engine/ is the branch's "
                  f"(tree {P['TIP_TREE']}); it differs from the built tree only in test code: engine/tests (ccb1d3b5) and #[cfg(test)] "
                  f"modules at the end of engine/src/hooks/core.rs ({P['TC']}). A rebuild with the latter gave the same three programs "
                  f"byte for byte ({CAND}/release/identity_N3.txt). The programs here are the candidate's tested bytes ({CAND}/programs/, "
                  f"the same git blobs), copied, never rebuilt."),
        'identity_evidence': (
            f"{CAND}/ (RESULT.md, games/summary.tsv, games/classify.tsv, games/u/, games/v/): the old pin's recorded games replayed on "
            f"the candidate, matched by pairing and game number with counts asserted (the research table's cells, kd3 and kpr3, "
            f"km3's coverage baselines, steps 8 and 8b, the 17 new cells, step 10's CLI, goldfish and run_screen, and Dustin's floor "
            f"pages 02, 06, 08, 10 and 14 and draft D's root and amended pages). 38 changed games in the recorded tables, all from the "
            f"Growl rule: 37 in new17 pairing 21 (g-mega_altaria_greninja v t-hydreigon) and 1 in step 8's km3 carrier pairing 11; the "
            f"build without the Growl commit (U) equals the old pin on every one. On the Rayquaza clause-(d) deals, played old v new, "
            f"1,260 of 12,000 games changed, all from #401 (the build without #401, V, equals the old pin on all 12,000). 0 unexplained. "
            f"Self-checks unchanged (km3 81b572198c04d5d1, kx3 31d638dbc818b0fa). Suite: 2,108 passed at the built commit, 2,125 with "
            f"the ported upstream tests, {P['SUITE']} with the two later test additions, 0 failed. The floor re-check pages of "
            f"rl/results/floor_recheck_rules2_2026-10/ replayed on the candidate deckgym: {P['FLOOR_SHORT']} ({CAND}/release/). "
            f"Engine source changes since main-c045ede: {len(src_changed)} files ({', '.join(f[len('engine/src/'):] for f in src_changed)}), "
            f"plus engine/UPSTREAM.md and test files; engine/src/players/, Cargo.lock and Cargo.toml unchanged."),
        'approved': P['APPROVED'],
        'purpose': (
            f"Official engine from {P['PIN']}: main-c045ede's engine (rules switch 2; the kta and km players) plus five engine commits: "
            f"the Growl-to-0 rule (an attack that an attacker-side effect cuts to 0 does 0, with no Weakness and no defender-side +X; "
            f"rules/05 #11), upstream #385 (on-play 'from your hand onto your Bench' Abilities only on the owner's turn), #390 (random "
            f"multi-hit damage in a fixed order), #401's Fossil part (DiscardFossil offered once) and #344 narrow (Dragon or Colorless "
            f"Energy zones invalid). engine/src/players/ is unchanged: km3 stays the working pilot on both sides of the screen and the "
            f"floor. No new revert switch: the engine reads the same {nsw} DECKGYM_* variables as main-c045ede, none set by default; set "
            f"one and the program is another engine, so never set one in a recorded run. The 0.7.2 RL add-on wheel and its run "
            f"identities are unchanged."),
    }
    m['latest_source_commit'] = BUILT
    m['latest_source_note'] = (f"engine/ is tracked in git. The available release ({NAME}) was built from this commit's engine/; later "
                               f"engine commits are newer source, not the release build. main's engine/ also carries test code the "
                               f"release build did not compile (engine/tests from ccb1d3b5, test modules in engine/src/hooks/core.rs "
                               f"from {P['TC']}); a rebuild with it gave the same programs.")
    text = json.dumps(m, indent=2, ensure_ascii=False) + '\n'
    json.loads(text)
    files['project_manifest.json'] = text

    # ---- rl/engine-2026-10-20/README.md --------------------------------------------------------------------------
    files[f'{NEW_DIR}/README.md'] = README.format(**P, NSW=nsw, BUILT=BUILT, NSRC=len(src_changed))

    # ---- START_HERE.md ------------------------------------------------------------------------------------------
    t = show('START_HERE.md')
    t = once(t, "`rl/engine-2026-10-12/` (`deckgym`, `legality_scan`, `goldfish`), main-c045ede: rules4",
             f"`{NEW_DIR}/` (`deckgym`, `legality_scan`, `goldfish`), {NAME}: rules4", 'START_HERE engine line')
    t = once(t, "; and since Oct 12 rules switch 2: round 2's coin-prevention rules and card-text fixes, Fossils as Item cards, and Weakness on an attack's return damage), with the km pilot",
             f"; since Oct 12 rules switch 2: round 2's coin-prevention rules and card-text fixes, Fossils as Item cards, and Weakness on an attack's return damage; and since {P['PIN_SHORT']} an attack cut to 0 by an attacker-side effect does 0 with no Weakness, plus upstream #385, #390, #401 (Fossil part) and #344 (narrow)), with the km pilot",
             'START_HERE engine line, history')
    files['START_HERE.md'] = t

    # ---- CLAUDE.md ----------------------------------------------------------------------------------------------
    t = show('CLAUDE.md')
    t = once(t, CLAUDE_OLD, CLAUDE_NEW.format(**P), 'CLAUDE.md engine paragraph')
    files['CLAUDE.md'] = t

    # ---- rl/RUN5.md ---------------------------------------------------------------------------------------------
    t = show('rl/RUN5.md')
    t = once(t, RUN5_421_OLD, RUN5_421_NEW.format(**P), 'RUN5 official engine')
    t = once(t, "kt presets replay the Sept 26-28 kt records.\n- **Pilot:** km3 = kta3 + N2",
             "kt presets replay the Sept 26-28 kt records.\n" + RUN5_PINNED.format(**P) + "- **Pilot:** km3 = kta3 + N2", 'RUN5 pinned bullets')
    t = once(t, "`results/floor_recheck_rules2_2026-10/` (planned and committed with the Oct 12 pin; if it fails, the floor isn't used until Dustin has seen the pages).",
             f"`results/floor_recheck_rules2_2026-10/` (planned and committed with the Oct 12 pin; if it fails, the floor isn't used until Dustin has seen the pages); its pages were replayed on {NAME}'s deckgym before the pin ({P['FLOOR_SHORT']}; `results/engine_candidate_2026-10-20/release/floor_recheck/`).",
             'RUN5 floor re-check')
    t = once(t, "  - The engine switches of Sept 25, 27, 28 and 30, the rules switch of Oct 1, and rules switch 2 (Oct 11-12).",
             f"  - The engine switches of Sept 25, 27, 28 and 30, the rules switch of Oct 1, rules switch 2 (Oct 11-12), and the Oct 20 engine candidate (pinned {P['PIN_SHORT']}).",
             'RUN5 switches list')
    t = once(t, "on the pinned engine `rl/engine-2026-10-12/` plus a card-effect pass", f"on the pinned engine `{NEW_DIR}/` plus a card-effect pass", 'RUN5 A5')
    files['rl/RUN5.md'] = t

    # ---- rules/ -------------------------------------------------------------------------------------------------
    t = show('rules/02_damage_knockouts_points.md')
    t = once(t, "  - **Engine:** it gave 20 for the Active hit until the fix on branch `claude/growl-zero-no-weakness`, not yet pinned; it already cut the Bench hit (`05` #11, `08` T7).",
             f"  - **Engine ✓ since {NAME} ({P['PIN_SHORT']}):** 0, no Weakness (it gave 20 for the Active hit before); it already cut the Bench hit (`05` #11, `08` T7). A defender-side \"+X damage\" effect is skipped too when the cut reaches 0: a stated choice with no recording, pinned by a test (`09`, \"Fixed {P['PIN_SHORT']}\").",
             'rules/02')
    files['rules/02_damage_knockouts_points.md'] = t
    t = show('rules/05_open_questions.md')
    t = once(t, "- **Engine:** it gave 20 here. The fix is on branch `claude/growl-zero-no-weakness`, not yet pinned. The text below is the earlier state of this question.",
             f"- **Engine ✓ since {NAME} ({P['PIN_SHORT']}):** 0 here, no Weakness (it gave 20 before; the fix came from branch `claude/growl-zero-no-weakness`). A defender-side \"+X damage\" effect is skipped too when the cut reaches 0: a stated choice with no recording, pinned by a test (`09`, \"Fixed {P['PIN_SHORT']}\"). The text below is the earlier state of this question.",
             'rules/05')
    files['rules/05_open_questions.md'] = t
    t = show('rules/08_tests_to_record.md')
    t = once(t, "The engine gave 20 for the Active hit; the fix is on branch `claude/growl-zero-no-weakness`.",
             f"The engine gave 20 for the Active hit; fixed in {NAME} ({P['PIN_SHORT']}).", 'rules/08')
    files['rules/08_tests_to_record.md'] = t
    t = show('rules/09_engine_repairs_2026-09-22.md')
    t = once(t, "\n## Fixed Oct 12 (rules switch 2, main-c045ede;", "\n" + RULES09_NEW.format(**P) + "\n## Fixed Oct 12 (rules switch 2, main-c045ede;", 'rules/09')
    files['rules/09_engine_repairs_2026-09-22.md'] = t

    # ---- make_predictions.py ------------------------------------------------------------------------------------
    p = 'rl/results/ladder_validation/make_predictions.py'
    t = show(p)
    t = once(t, MP_OLD, MP_NEW.format(**P), 'make_predictions CURRENT_ENGINE')
    t = once(t, "def selftest(repo, use_git=True):\n    fails = []\n", MP_SELFTEST, 'make_predictions selftest')
    files[p] = t
    p = 'rl/results/ladder_validation/read_ladder.py'
    t = show(p)
    t = once(t, "def selftest(repo, export, use_git=True):\n    fails = []\n", RL_SELFTEST, 'read_ladder selftest')
    files[p] = t

    # ---- rl/deck_journal/test_journal.py ------------------------------------------------------------------------
    p = 'rl/deck_journal/test_journal.py'
    t = show(p)
    t = once(t, "import tempfile\nimport unittest\n", "import tempfile\nimport unittest\nfrom unittest import mock\n", 'test_journal import')
    t = once(t, TJ_OLD, TJ_NEW, 'test_journal replay-B')
    t = once(t, TJ_VIEW_OLD, TJ_VIEW_NEW, 'test_journal deck-01 view')
    files[p] = t

    # ---- the release notes (with the draft; rl/engine-2026-10-20/README.md points at them) ------------------------
    files[f'{CAND}/RELEASE_NOTES.md'] = NOTES.format(**P, IDENT=V['ident'], FLOOR_TABLE=V['floor_table'], FLOOR_SORT=V['floor_sort'],
                                                      SLOWPIN_NOTES=V['slowpin_notes'], DRAFT_CHECKS=V['draft_checks'])

    # ---- build the commit from a private index ------------------------------------------------------------------
    for path, text in files.items():
        if '\r' in text:
            sys.exit(f'{path}: CR in the new text')
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(td, 'index'))
        git('read-tree', base, env=env)
        for path, text in files.items():
            blob = gs('hash-object', '-w', '--stdin', inp=text.encode('utf-8'))
            git('update-index', '--add', '--cacheinfo', f'100644,{blob},{path}', env=env)
        for n, (sha, blob) in PROGS.items():
            git('update-index', '--add', '--cacheinfo', f'100755,{blob},{NEW_DIR}/{n}', env=env)
        git('update-index', '--add', '--cacheinfo', f'100644,{SUMS_BLOB},{NEW_DIR}/SHA256SUMS', env=env)
        tree = gs('write-tree', env=env)
    diff = gs('diff-tree', '-r', '--name-status', base, tree).splitlines()
    exists = lambda p: subprocess.run(['git', '-C', REPO, 'cat-file', '-e', f'{base}:{p}'], capture_output=True).returncode == 0
    want_diff = sorted([f'A\t{NEW_DIR}/{n}' for n in ('README.md', 'SHA256SUMS', 'deckgym', 'goldfish', 'legality_scan')] +
                       [('M' if exists(p) else 'A') + f'\t{p}' for p in files if not p.startswith(NEW_DIR)])
    if sorted(diff) != want_diff:
        sys.exit(f'unexpected tree diff:\n' + '\n'.join(sorted(diff)))
    modes = gs('ls-tree', tree, NEW_DIR + '/')
    if '--dry-run' in sys.argv:
        print(f'DRY RUN: tree {tree} on base {base[:8]}; {len(diff)} paths:\n' + '\n'.join(diff) + '\n' + modes)
        print('placeholders:', sorted(set(re.findall(r'@@[^@]+@@', ''.join(files.values())))))
        out = os.environ.get('ADOPT_DUMP')
        if out:
            for path, text in files.items():
                dst = os.path.join(out, path)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, 'w', encoding='utf-8', newline='\n').write(text)
        return
    msg = COMMIT_MSG.format(**P, BASE=base[:8])
    commit = gs('-c', 'user.name=dacz8976-creator', '-c', 'user.email=dacz8976@gmail.com', 'commit-tree', tree, '-p', base, '-F', '-',
                inp=msg.encode())
    ref = f'refs/heads/{branch}'
    cur = subprocess.run(['git', '-C', REPO, 'rev-parse', '-q', '--verify', ref], capture_output=True, text=True).stdout.strip()
    if cur and not replace:
        sys.exit(f'{branch} exists ({cur[:8]}); pass --replace to move it')
    git('update-ref', ref, commit, *([cur] if cur else ['']))
    left = sorted(set(re.findall(r'@@[^@]+@@', ''.join(files.values()))))
    print(f'draft {commit} on {branch} (parent {base[:8]}, tree {tree[:8]}); {len(diff)} paths:')
    print('\n'.join(diff))
    print(modes)
    print('placeholders left for the adoption:', left)


README = """# The official engine from {PIN_SHORT}: main-d9d2e70 (the Growl-to-0 rule and four upstream fixes)

- **Programs:** `deckgym`, `legality_scan`, `goldfish`; sha256 in `SHA256SUMS` and `project_manifest.json`. Linux (WSL or the cloud). Committed with the executable bit (git mode 100755), so a Linux clone runs them as they are.
  - `deckgym` 245e11e8cf939da7ba12a50fbb18630c67b1fb2231a692dd0c259c4a01556745
  - `legality_scan` bce5654bb51b8b8bc201fba353267c575c168291959c32de6ee1365ecf7db8e9
  - `goldfish` f53e948997326174103d917642cde78edb788098a7e8a5faf702096c91390e35
  - These are the programs the candidate pass built and tested, copied and never rebuilt (`../results/engine_candidate_2026-10-20/programs/`, the same git blobs).
- **Built** in WSL on Oct 20 (02:09-02:18 UTC) from one `git archive` of {BUILT} (branch `laptop/engine-candidate-2026-10-20`), whose `engine/` tree is 12e23abd. `cargo build --release --locked`, `--example legality_scan`, `--example goldfish`, in a fresh folder with an empty target directory, CARGO_BUILD_JOBS 2, 527 s (`../results/engine_candidate_2026-10-20/RESULT.md`, `tests_and_builds.txt`).
  - **Test code is the only difference from main's `engine/`.** main's `engine/` is the branch's (tree {TIP_TREE}), not the built tree 12e23abd: `engine/tests/` (ccb1d3b5, the ported upstream tests: 3 files changed, 7 added) and two `#[cfg(test)]` additions at the end of `engine/src/hooks/core.rs` ({TC}: the Growl "+X" pin and the Poltchageist turn test). Everything else in `engine/` (`src` before its first test module, `examples`, `Cargo.toml`, `Cargo.lock`, `database.json`) is the built commit's. A rebuild with the `hooks/core.rs` additions gave the same three programs byte for byte (`../results/engine_candidate_2026-10-20/release/identity_N3.txt`).
- **What it is:** main-c045ede's engine (`../engine-2026-10-12/`) plus five engine commits (`../results/engine_candidate_2026-10-20/PLAN.md`, written before the build, and `RESULT.md`; `rules/09`, "Fixed {PIN_SHORT}"):
  - **The Growl-to-0 rule** (501fc1dd): an attack that an attacker-side effect (Growl, Teary Attack and the like) cuts to 0 does 0: no Weakness, and the Bench hit is cut too, as recorded on Oct 19 (`rules/02` §1, §3; `rules/05` #11). A defender-side "+X damage" effect is skipped as well when the cut reaches 0: a stated choice with no recording, pinned by a test.
  - **Upstream #385** (9c51453b): "Once during your turn, when you put this Pokémon from your hand onto your Bench" Abilities (Miraidon ex, Roaring Moon, Poltchageist) are offered only on the owner's turn: not in setup, and not when the opponent's Team Rocket's Boss benches the Pokémon.
  - **Upstream #390** (75343578): random multi-hit damage is enumerated in a fixed order, so a replay is deterministic.
  - **Upstream #401, the Fossil part** (42d2dd8e): DiscardFossil is offered once, not twice.
  - **Upstream #344, narrow** (764f7459): a deck whose Energy zone holds Dragon or Colorless Energy is invalid, with a named panic.
  - d9d2e704 refreshes `engine/UPSTREAM.md` (a doc; its line 9 still says "NOT adopted", left so `engine/` does not change again at the pin).
  - {NSRC} source files change (`../results/engine_candidate_2026-10-20/RESULT.md`). The suite: 2,108 passed at d9d2e704, 2,125 with the ported tests, {SUITE} with the two later test additions; 0 failed each time.
- **Revert switches:** none new. The engine reads the same {NSW} `DECKGYM_*` environment variables as main-c045ede (the 13 of rules switch 2 and the older `DECKGYM_UNBOUNDED_ENERGY_MOVES`), none set by default. Set one and the program is another engine: never set one in a recorded run. None of the five changes has a switch.
- **What didn't change: the players.** `engine/src/players/`, `Cargo.lock` and `Cargo.toml` are unchanged. km3 stays the working pilot, on both sides of the screen and the floor.
- **Evidence** (`../results/engine_candidate_2026-10-20/RESULT.md`; every replay matched by pairing and game number, counts asserted):
  - The old pin's recorded games replayed on the candidate: the research table's cells, kd3 and kpr3, km3's coverage baselines (B2e's 96 pairings, the second lists, Scizor), steps 8 and 8b, the 17 new cells, step 10 (CLI, goldfish, run_screen) and Dustin's floor pages 02, 06, 08, 10 and 14 and draft D's root and amended pages.
  - **38 changed games in the recorded tables, all from the Growl rule:** 37 in new17 pairing 21 (g-mega_altaria_greninja v t-hydreigon: Bonsly's Teary Attack cuts Deino's and Bombirdier's attacks into the Darkness-weak Oricorio to 0) and 1 in step 8's km3 carrier rows (pairing 11). The build without the Growl commit (U) equals the old pin on every one.
  - **1,260 changed games of 12,000 on the Rayquaza clause-(d) deals, played old v new, all from #401:** the list holds Skull Fossil; km3 629, kta3 621, k3 10 of 4,000 each; the deck's paired average score moves by at most +0.0022 (se 0.0031). The build without #401 (V) equals the old pin on all 12,000.
  - **0 unexplained.** The self-checks are unchanged: km3 81b572198c04d5d1, kx3 31d638dbc818b0fa.
  - **The floor re-check pages** of `../results/floor_recheck_rules2_2026-10/` replayed on the candidate deckgym before the pin: {FLOOR_LONG} (`../results/engine_candidate_2026-10-20/release/floor_recheck/`).
- **Approved:** {APPROVED}. Astra's review (Oct 20, agent mailbox): no implementation defect; adoption after the Growl "+X" choice is resolved and the release follow-through is done.
- **What stays on the old engine:** kx3 and its recorded games, the mixed kt/kta clause-(d) tables (ec7e1a8), scoreboard v3's frozen cells and thresholds and kta3's status, the ladder predictions, exam run 1 and the frozen judge, and the slow report until its re-pin: none is re-run here, none is new-engine evidence, and old thresholds and summaries do not carry over (`../results/engine_candidate_2026-10-20/RELEASE_NOTES.md` has the full list).
- **Known limits** (for a later round; `RESULT.md`, "Open points for the reviewer"):
  - The Growl "+X" choice has no recording, and no listed deck reaches it.
  - #390's tests compare sorted outcomes; the fixed order rests on the BTreeMap in the code.
  - #344 makes two research deck files invalid (`../results/limitless_skill_model_2026-09-25/decklists/garchomp.txt`, `raticate_ninetales.txt`), and the CLI's message for that rejection is the generic "failed full-deck validation".
  - The recorded kt/kta clause-(d) tables (ec7e1a8) were not replayed; #401 would very likely change them.
  - A hit back still ignores the attacker's own cards (`rules/09`, open).
- **History:** `../engine-2026-10-12/` (main-c045ede) and earlier are kept unchanged, with their hashes in the manifest's historical releases.
"""

CLAUDE_OLD = """- The official engine program is `rl/engine-2026-10-12/deckgym` (since Oct 12; main-c045ede: rules switch 2,
  round 2's coin-prevention rules on top of main-8626a35, with the card-text fixes, Fossils as Item cards and Weakness
  on an attack's return damage; `engine/src/players/` unchanged; `rl/engine-2026-10-12/README.md`). The working pilot
  is km3, on both sides of the screen and the floor. Since Sept 30, kt3/kta3/ktb3/ktc3 name the kog-based presets
  (kt3, ktb3 and ktc3 are diagnostic only). Earlier programs (`rl/engine-2026-10-02/`, `-09-30/`, `-09-28/`, `-09-27/`,
  `-09-25/`, `rl/addon-0.7.2/deckgym`) are history; the verified add-on 0.7.2 wheel (`rl/addon-0.7.2/wheels/`) is
"""
CLAUDE_NEW = """- The official engine program is `rl/engine-2026-10-20/deckgym` (since {PIN_SHORT}; main-d9d2e70: main-c045ede's
  engine plus the Growl-to-0 rule (an attack cut to 0 by an attacker-side effect does 0, no Weakness) and upstream #385,
  #390, #401 (Fossil part) and #344 (narrow); `engine/src/players/` unchanged; `rl/engine-2026-10-20/README.md`). The working pilot
  is km3, on both sides of the screen and the floor. Since Sept 30, kt3/kta3/ktb3/ktc3 name the kog-based presets
  (kt3, ktb3 and ktc3 are diagnostic only). Earlier programs (`rl/engine-2026-10-12/`, `-10-02/`, `-09-30/`, `-09-28/`,
  `-09-27/`, `-09-25/`, `rl/addon-0.7.2/deckgym`) are history; the verified add-on 0.7.2 wheel (`rl/addon-0.7.2/wheels/`) is
"""

RUN5_421_OLD = ("- **Official engine:** `rl/engine-2026-10-12/`, main-c045ede (pinned Oct 12; rules switch 2: the Oct 2 engine plus round 2's "
                "coin-prevention rules and card-text fixes, Fossils as Item cards and Weakness on an attack's return damage; "
                "`engine/src/players/` unchanged). kta3, km3, k3, kp3 and kog3 (and kq3, kpr3 and kd3) replay their recorded games game "
                "for game, k3 and kp3 on all 45 cells, every changed game is accounted for, and km3's B2e reference for the 16 two-Ariados "
                "pairings is step 9's replay (`results/engine_switch_rules2_2026-10/`). kt3, ktb3 and ktc3 are kog-based: diagnostic, no "
                "identity claim. The Oct 2 engine (`rl/engine-2026-10-02/`, main-8626a35),")
RUN5_421_NEW = ("- **Official engine:** `rl/engine-2026-10-20/`, main-d9d2e70 (pinned {PIN_SHORT}; main-c045ede's engine plus the Growl-to-0 "
                "rule and upstream #385, #390, #401 (Fossil part) and #344 (narrow); `engine/src/players/` unchanged). Replaying the old "
                "pin's recorded games changed 38, all from the Growl rule (37 in new17 pairing 21, 1 in step 8's km3 carrier rows), and "
                "1,260 of the 12,000 Rayquaza clause-(d) games played old v new, all from #401; 0 unexplained; every other replayed row "
                "is equal (`results/engine_candidate_2026-10-20/RESULT.md`). The pairing-21 and carrier references, scoreboard v3's frozen "
                "cell, kta3's status and km3's thresholds stay main-c045ede's until Dustin decides the re-baselining "
                "(`results/engine_candidate_2026-10-20/RELEASE_NOTES.md`). kt3, ktb3 and ktc3 are kog-based: diagnostic, no identity "
                "claim. Rules switch 2's engine (`rl/engine-2026-10-12/`, main-c045ede; `results/engine_switch_rules2_2026-10/`), the "
                "Oct 2 engine (`rl/engine-2026-10-02/`, main-8626a35),")
RUN5_PINNED = """  - **Pinned {PIN_SHORT}** (`results/engine_candidate_2026-10-20/`: PLAN.md, written before the build; RESULT.md; RELEASE_NOTES.md). Dustin (verbatim): {APPROVED}. Astra's review (Oct 20): no implementation defect; adoption after the Growl "+X" choice and the release follow-through.
    - Not re-run and not new-engine evidence (they stay main-c045ede's; old thresholds and summaries do not carry over): kx3 and its recorded games, the mixed kt/kta clause-(d) tables (ec7e1a8), scoreboard v3's frozen cells and thresholds and kta3's status, the ladder predictions (never overwritten), exam run 1 and the frozen judge.
    - The slow report: {SLOWPIN_RUN5}.
"""

RULES09_NEW = """## Fixed {PIN_SHORT} (main-d9d2e70; plan and evidence in `rl/results/engine_candidate_2026-10-20/`; the hit-back entry above stays open)

- **An attack cut to 0 by an attacker-side effect does 0** (501fc1dd, from branch `claude/growl-zero-no-weakness`): no Weakness on the Active, and the Bench hit is cut too, as the Oct 19 recording Growl_weakness_test showed (`02` §1/§3, `05` #11, `08` T7). Before, the engine gave 0 + 20 Weakness. A defender-side "+X damage" effect is skipped as well when the cut reaches 0: a stated choice, not recorded; `a_defender_side_plus_x_is_also_skipped_when_the_cut_reaches_zero` (`engine/src/hooks/core.rs`) pins it.
- **Upstream #385** (9c51453b): "Once during your turn, when you put this Pokémon from your hand onto your Bench" Abilities (Miraidon ex, Roaring Moon, Poltchageist) are offered only on the owner's turn: not in setup, and not when the opponent's Team Rocket's Boss benches the Pokémon. Tests: the ported upstream ones (Miraidon ex, Roaring Moon, a Team Rocket's Boss case) and Poltchageist's on-turn and off-turn tests (`engine/src/hooks/core.rs`).
- **Upstream #390** (75343578): random multi-hit damage is enumerated in a fixed order, so replays are deterministic.
- **Upstream #401, the Fossil part** (42d2dd8e): DiscardFossil was offered twice; it is offered once.
- **Upstream #344, narrow** (764f7459): a deck whose Energy zone holds Dragon or Colorless Energy is invalid (a named panic). Two research deck files without an "Energy:" line become invalid (`rl/results/limitless_skill_model_2026-09-25/decklists/garchomp.txt`, `raticate_ninetales.txt`).
"""

MP_OLD = """CURRENT_ENGINE = {
    "label": "rules switch 2 (main-c045ede, pinned Oct 12)",
    "harness_engine_trees": ["4ebb30a94173"],          # slow reports / exams: "engine tree <12 hex>" in manifest.json
    "floor_engines": ["rl/engine-2026-10-12/deckgym"],  # floor pages: "- Engine: <path>"
}
"""
MP_NEW = """CURRENT_ENGINE = {{
    "label": "main-d9d2e70 (the Growl-to-0 rule and four upstream fixes, pinned {PIN_SHORT})",
    "harness_engine_trees": [],                         # slow reports / exams: "engine tree <12 hex>" in manifest.json (none until the slow report's re-pin)
    "floor_engines": ["rl/engine-2026-10-20/deckgym"],  # floor pages: "- Engine: <path>"
}}
# The Oct 12 pin's value. Deck 12's self-test reads files written under it, so it runs with this one.
CURRENT_ENGINE_OCT12 = {{
    "label": "rules switch 2 (main-c045ede, pinned Oct 12)",
    "harness_engine_trees": ["4ebb30a94173"],
    "floor_engines": ["rl/engine-2026-10-12/deckgym"],
}}
"""
MP_SELFTEST = """def selftest(repo, use_git=True):
    # Deck 12's real files were written under the Oct 12 pin: its checks expect that pin's CURRENT_ENGINE.
    global CURRENT_ENGINE
    saved, CURRENT_ENGINE = CURRENT_ENGINE, CURRENT_ENGINE_OCT12
    try:
        return _selftest(repo, use_git)
    finally:
        CURRENT_ENGINE = saved


def _selftest(repo, use_git=True):
    fails = []
"""

RL_SELFTEST = """def selftest(repo, export, use_git=True):
    # The snapshot's deck-12 predictions were made under the Oct 12 pin: build and read them under its CURRENT_ENGINE.
    saved, mp.CURRENT_ENGINE = mp.CURRENT_ENGINE, mp.CURRENT_ENGINE_OCT12
    try:
        return _selftest(repo, export, use_git)
    finally:
        mp.CURRENT_ENGINE = saved


def _selftest(repo, export, use_git=True):
    fails = []
"""

TJ_OLD = """    def test_replay_b_files_under_deck01_with_both_bots_on_the_current_engine(self):
        doc = kingambit_doc()
        res = J.add_bot(doc, ROOT, "35d98d0dcaf2", REPLAY_B, by="test")
"""
TJ_NEW = """    def test_replay_b_files_under_deck01_with_both_bots_on_the_current_engine(self):
        # REPLAY_B was played on the Oct 12 pin's engine: current under that pin's CURRENT_ENGINE.
        doc = kingambit_doc()
        with mock.patch.object(J.mp, "CURRENT_ENGINE", J.mp.CURRENT_ENGINE_OCT12):
            res = J.add_bot(doc, ROOT, "35d98d0dcaf2", REPLAY_B, by="test")
"""
TJ_VIEW_OLD = """    def test_deck01_bot_numbers_never_appear_under_his_list_and_the_view_is_repeatable(self):
        doc = kingambit_doc()
        J.add_bot(doc, ROOT, "35d98d0dcaf2", REPLAY_B, by="test")
"""
TJ_VIEW_NEW = """    def test_deck01_bot_numbers_never_appear_under_his_list_and_the_view_is_repeatable(self):
        doc = kingambit_doc()
        with mock.patch.object(J.mp, "CURRENT_ENGINE", J.mp.CURRENT_ENGINE_OCT12):  # REPLAY_B: the Oct 12 pin's engine
            J.add_bot(doc, ROOT, "35d98d0dcaf2", REPLAY_B, by="test")
"""

NOTES = """# Release notes: main-d9d2e70, the engine candidate of Oct 20 (DRAFT: not adopted)

**Not adopted.** This file comes with the adoption draft on `laptop/engine-adoption-draft-2026-10-20`; main is untouched, and the adoption waits for Dustin's yes. His open calls: the Growl rule's defender-side "+X" choice (the recommendation is to keep it as an accepted uncertainty, now pinned by a test), #385 as a rule, and the re-baselining in item 3 below.

## What the adoption activates
- **The three programs** in `rl/engine-2026-10-20/` (`deckgym` 245e11e8…, `legality_scan` bce5654b…, `goldfish` f53e9489…): the candidate's tested bytes, the same git blobs as `programs/` here, mode 100755, never rebuilt.
- **The current-engine selector.** `project_manifest.json`'s `available_release` names them. `current_engine.py`, `decks/screen/floor.py` and `decks/screen/run_screen.py` read it, so the screen and the floor switch with the manifest. `make_predictions.py`'s `CURRENT_ENGINE` moves with it: floor pages made on `rl/engine-2026-10-20/deckgym` count as current, and no slow report does until the slow report's re-pin.
- **The slow-report program:** {SLOWPIN_NOTES}

## Release identity
- Built from d9d2e704 (engine tree 12e23abd) on Oct 20, 02:09-02:18Z.
- The branch's `engine/` differs from the built tree in test code only:
  - c1670e81 (the candidate's result commit): engine tree 300030ce = 12e23abd plus `engine/tests/` (ccb1d3b5: 3 files changed, 7 added);
  - {TC}: two `#[cfg(test)]` additions at the end of `engine/src/hooks/core.rs` (the Growl "+X" pin, and Poltchageist's on-turn and off-turn tests); engine tree {TIP_TREE}.
  - {IDENT}
- **Activation checks** (after the merge, in the repository root, on Linux):
  1. `cd rl/engine-2026-10-20 && sha256sum -c SHA256SUMS`: three OK lines.
  2. `git ls-tree HEAD rl/engine-2026-10-20/`: deckgym 2d5c1673…, legality_scan a0bfd36c…, goldfish 8b6739ab…, each 100755.
  3. `python3 current_engine.py`: prints this repository's `rl/engine-2026-10-20/deckgym` (it refuses a file whose hash is not the manifest's).
  4. The manifest's three sha256 equal `SHA256SUMS`.

## The floor re-check pages, replayed on the candidate
{FLOOR_TABLE}

{FLOOR_SORT}

## Tied to the OLD engine (main-c045ede): not re-run, and not new-engine evidence
Old thresholds and summaries do not carry over. Each item stays a record of main-c045ede (or of an older engine):
1. **kx3 and its recorded games.** The slow-report pin (program 76df495b; laptop/kx3-on-rules2 cd20a97a, engine tree 4ebb30a9) until its re-pin; the 8 slow reports made on it (`rl/results/slow_reports/2026-10-12_*`, `2026-10-13_*`, `2026-10-14_*`) and the paired dry runs; `kx3_on_rules2_2026-10/` (its 202 + 202 replay games), `m64_on_rules2_2026-10/` and `pause_positions_kx3_2026-10/`. kx3's unchanged self-check digest is a 12-game check, not identity for those games.
2. **The mixed kt/kta clause-(d) tables (ec7e1a8):** `kt_tables_2026-09-28/ec7e1a8_d_*` and `ec7e1a8_mixed_*`, `kta_tables_2026-09-29/ec7e1a8_fresh_d_*` and `ec7e1a8_fresh_id_*_d_i20`. Not replayed. On the same deals #401 changed 15.7% of km3's and 15.5% of kta3's Rayquaza games, so these would very likely change.
3. **Scoreboard v3's frozen cells and thresholds, and kta3's status.** `scoreboard_v3_2026-09-27/frozen_cells.csv` (its altaria_greninja v hydreigon cell holds new17 pairing 21, where k3 changes 8 and kp3 7 of 500 games), RUN5's development real error (k3 15.3, kp3 15.5, kog3 14.0), kta3's "adopted, unconfirmed" status and km3's Stadium thresholds (`km_tables_2026-09-30/READING.md`). The re-baselining is Dustin's decision (the precedent is switch 2's PLAN, question 3a). The would-be new references are the candidate's 7 game files in `games/new/`; their names keep the `08a9b3a_` prefix of the commands they replay, but the candidate played them.
4. **The ladder predictions** (`rl/results/ladder_validation/predictions/`, 8 files), never overwritten. After the pin `read_ladder.py` prints "NOT the current engine now" for them; new-engine predictions are new files, from new-engine pages and reports.
5. **Exam run 1 and the frozen AI judge** (frozen-4, engine 70652fff; `weekly_review_2026-10-18/RUN1_OUTCOME.md`). A later run on this engine needs a new freeze (frozen-5).
6. **The Oct 12 floor re-check pages** (`floor_recheck_rules2_2026-10/`) and their runners. The candidate's pages above are new records beside them, never replacements.
7. **Also on the old engine:** the deck journal's stored "current engine" flags (deck 01's two kx3/km3 entries mean "current when added"); the pg_pos position harnesses and the pause-game position lists (`next_pilot_2026-10/old_positions/`, `pause_games_new_2026-10-12/` and `-13/`); the setup tester's runs (labelled c045ede; probably unaffected, not checked); dated prose naming main-c045ede or `rl/engine-2026-10-12/` (history, left as is). One of those can mislead a reader: `deck_improvement/kingambit_2026-10-15/CHECK.md:359` says to use `rl/engine-2026-10-12/deckgym`.

What carries over unchanged: every replayed row that came out equal (the research table's cells, B2e's 96 pairings, Scizor, the second lists, step 10's CLI, goldfish and run_screen, Dustin's floor pages 02, 06, 08, 10 and 14 and draft D's root and amended pages).

## Checks of the draft (a scratch worktree; no engine run)
{DRAFT_CHECKS}

## Left as is on purpose
- `engine/UPSTREAM.md` line 9 still says "NOT adopted". Editing it would change `engine/` again at the pin; RUN5, this file and `rl/engine-2026-10-20/README.md` record the adoption.
- The candidate's U and V builds (local refs, not pushed) and the laptop's `pincand_work` stay until the adoption is decided.
"""

COMMIT_MSG = """DRAFT, NOT ADOPTED: pin the engine candidate as main-d9d2e70 (rl/engine-2026-10-20/)

The adoption commit, drafted for Dustin's yes; not on main, not to be merged without it. The @@...@@
placeholders (the pin date and his words) are filled by re-running the generator at adoption
(rl/results/engine_candidate_2026-10-20/release/adopt_draft.py). Parent {BASE}.

- rl/engine-2026-10-20/: the candidate's tested programs (deckgym 245e11e8, legality_scan bce5654b,
  goldfish f53e9489; the same blobs as programs/, mode 100755), SHA256SUMS, README.md.
- project_manifest.json: main-c045ede moves to historical_releases (superseded); available_release is
  main-d9d2e70 (source_commit d9d2e704, the built commit); latest_source_*.
- START_HERE.md and CLAUDE.md pin lines, rl/RUN5.md, rules/02, 05, 08 ("not yet pinned" lines) and 09
  ("Fixed" section).
- make_predictions.py CURRENT_ENGINE moves (no slow-report tree until the re-pin); its deck-12 self-test
  and read_ladder.py's self-test run under the Oct 12 value. test_journal's two tests that add REPLAY_B (played on the Oct 12 engine)
  add it under the Oct 12 value.

Release notes, in this commit: rl/results/engine_candidate_2026-10-20/RELEASE_NOTES.md.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
"""

if __name__ == '__main__':
    main()
