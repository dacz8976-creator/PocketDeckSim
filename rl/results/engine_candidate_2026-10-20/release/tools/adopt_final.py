#!/usr/bin/env python3
"""Draft (do NOT adopt) the adoption commit for the FINAL engine candidate (PLAN addendum, items 8-10): main-<F7> in
VARS["engine_dir"], built from VARS["f_commit"].

  adopt_final.py VARS.json [--replace] [--dry-run]

One commit on top of VARS["base"] (the candidate branch tip, which must hold main's latest commit and whose engine/ must be
the built commit's, byte for byte), from a private index: nothing checked out, refs/heads/main never touched, nothing
pushed. The programs are the final build's tested blobs, already committed on the branch in VARS["progs_dir"].
Files: ENGINE_DIR/{deckgym,legality_scan,goldfish} (mode 100755), SHA256SUMS, README.md; project_manifest.json;
START_HERE.md, CLAUDE.md, rl/RUN5.md; rules/02, 04, 05, 08, 09; make_predictions.py's CURRENT_ENGINE (its deck-12 self-test
and read_ladder.py's under the Oct 12 value); test_journal.py's two REPLAY_B tests under the Oct 12 value; RELEASE_NOTES.md.
The pin date and Dustin's words are @@...@@ placeholders unless VARS gives them. Every edit replaces text that must occur
exactly once."""
import hashlib, json, os, re, subprocess, sys, tempfile

REPO = '/home/dacz8976/pincand'
OFFICIAL = 'c045ede0e6d69c9dcb8d4cb3165c8ada3f8ef72e'
C_BUILT = 'd9d2e70458273b77c379a7424ad33a162289205a'
CAND = 'rl/results/engine_candidate_2026-10-20'
OLD = dict(name='main-c045ede', dir='rl/engine-2026-10-12',
           deckgym='0a9199bca480acf6f862342e042b7f36bb885416659eafeef24485c1783158c4',
           legality_scan='bf9d75020558b843a4f71d80a848d9150daff44e34f3b2159c16539b015a0ec7',
           goldfish='d8cfb7799770e16623c5d5ddc47b3ce55a714d66ec541fa8eb476a77fcf79a84')
ORDER = ('deckgym', 'legality_scan', 'goldfish')


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


def main():
    V = json.load(open(sys.argv[1]))
    base = gs('rev-parse', V['base'] + '^{commit}')
    F = gs('rev-parse', V['f_commit'] + '^{commit}')
    main_c = gs('rev-parse', V['main'] + '^{commit}')
    NAME = 'main-' + F[:7]
    NEW_DIR = V['engine_dir']
    PD = V['progs_dir']
    branch = V.get('branch', 'laptop/engine-adoption-draft-2026-10-20')
    P = dict(
        NAME=NAME, NEW_DIR=NEW_DIR, PD=PD, F=F, F8=F[:8], FTREE=gs('rev-parse', F + ':engine')[:8],
        PIN=V.get('pin_date') or '@@PIN_DATE@@', PIN_SHORT=V.get('pin_short') or '@@PIN_DATE_SHORT@@',
        APPROVED=V.get('approved') or "@@APPROVED: Dustin's words, verbatim, with the date@@",
        BUILT_AT=V['built_at'], SUITE=V['suite_count'], ITEM8=V['item8_commit'][:8], TESTS=V['tests_commit'][:8],
        FLOOR_SHORT=V['floor_short'], FLOOR_LONG=V['floor_long'], REPLAYS=V['replays_short'], SLOWPIN_RUN5=V['slowpin_run5'],
    )

    # ---- guards --------------------------------------------------------------------------------------------------
    for a, b, what in ((OFFICIAL, F, 'main-c045ede'), (C_BUILT, F, 'the Oct 20 built commit'), (F, base, 'F'), (main_c, base, 'main')):
        if subprocess.run(['git', '-C', REPO, 'merge-base', '--is-ancestor', a, b]).returncode:
            sys.exit(f'{what} ({a[:8]}) is not an ancestor of {b[:8]}')
    if gs('rev-parse', 'origin/main') != main_c:
        sys.exit('origin/main is not VARS["main"]: re-take the base texts')
    if gs('rev-parse', base + ':engine') != gs('rev-parse', F + ':engine'):
        sys.exit("the base's engine/ is not the built commit's")
    for d in ('engine/Cargo.toml', 'engine/Cargo.lock', 'engine/src/players'):
        if gs('rev-parse', f'{OFFICIAL}:{d}') != gs('rev-parse', f'{F}:{d}'):
            sys.exit(f'{d} changed since main-c045ede')
    sw = lambda c: sorted(set(re.findall(r'DECKGYM_[A-Z0-9_]+', gs('grep', '-h', '-o', r'DECKGYM_[A-Z0-9_]*', c, '--', 'engine/src'))))
    if sw(F) != sw(OFFICIAL):
        sys.exit('the built commit reads a different set of DECKGYM_* switches than main-c045ede')
    nsw = len(sw(F))
    src_changed = [f for f in gs('diff', '--name-only', OFFICIAL, F, '--', 'engine/src').splitlines()]
    progs = {}
    for n in ORDER:
        line = gs('ls-tree', base, f'{PD}/{n}')
        m_ = re.fullmatch(r'100755 blob ([0-9a-f]{40})\t' + re.escape(f'{PD}/{n}'), line)
        if not m_:
            sys.exit(f'{PD}/{n}: {line!r}')
        sha = hashlib.sha256(git('cat-file', 'blob', m_.group(1))).hexdigest()
        progs[n] = (sha, m_.group(1))
    sums_blob = gs('rev-parse', f'{base}:{PD}/SHA256SUMS')
    if git('cat-file', 'blob', sums_blob).decode() != ''.join(f'{progs[n][0]}  {n}\n' for n in ORDER):
        sys.exit('SHA256SUMS does not match the committed programs')
    if V.get('expect_deckgym') and progs['deckgym'][0] != V['expect_deckgym']:
        sys.exit('deckgym is not the expected build')
    if gs('ls-tree', base, NEW_DIR):
        sys.exit(f'{NEW_DIR} exists in the base')
    P.update({f'{n.upper()}_SHA': progs[n][0] for n in ORDER})
    P.update({f'{n.upper()}_BLOB': progs[n][1][:8] for n in ORDER})
    P.update(NSW=nsw, NSRC=len(src_changed), SRC=', '.join(f[len('engine/src/'):] for f in src_changed))

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
    hist['superseded'] = (f"{P['PIN']} by {NAME} (the Growl-to-0 rule, the hit back as attack damage, and upstream #385, #390, "
                          f"#401 Fossil part, #344 narrow, #367/#418; {NEW_DIR}/)")
    m['historical_releases'].append(hist)
    m['available_release'] = {
        'name': NAME,
        'artifact': f'{NEW_DIR}/deckgym', 'sha256': progs['deckgym'][0],
        'legality_scan': f'{NEW_DIR}/legality_scan', 'legality_scan_sha256': progs['legality_scan'][0],
        'goldfish': f'{NEW_DIR}/goldfish', 'goldfish_sha256': progs['goldfish'][0],
        'goldfish_note': old['goldfish_note'],
        'source_commit': F,
        'source_working_tree': False,
        'built': (f"{P['BUILT_AT']} in WSL: cargo build --release --locked, --example legality_scan and --example goldfish, from one "
                  f"git archive of {F} (branch laptop/engine-candidate-2026-10-20: main-c045ede's engine plus six engine changes; "
                  f"engine/ tree {P['FTREE']}), in a fresh folder with an empty target directory, CARGO_BUILD_JOBS 2 "
                  f"({CAND}/release/build_F.log). source_commit is the built commit itself, and main's engine/ is byte-identical "
                  f"to it. The programs here are the tested bytes ({PD}/, the same git blobs), copied, never rebuilt."),
        'identity_evidence': (
            f"{CAND}/: (1) the Oct 20 candidate pass (RESULT.md) on the build of d9d2e704 (deckgym 245e11e8): the old pin's "
            f"recorded games replayed, matched by pairing and game number with counts asserted; 38 changed games in the recorded "
            f"tables, all from the Growl rule (37 in new17 pairing 21, 1 in step 8's km3 carrier pairing 11; the build without "
            f"the Growl commit, U, equals the old pin on each), and 1,260 of 12,000 Rayquaza clause-(d) games played old v new, "
            f"all from #401 (the build without #401, V, equals the old pin on all); 0 unexplained. (2) The final build, which is "
            f"that build plus the hit back as attack damage (PLAN addendum, item 8) and tests: the floor re-check pages of "
            f"rl/results/floor_recheck_rules2_2026-10/, {P['FLOOR_SHORT']}; a sample of the candidate pass's runs, {P['REPLAYS']} "
            f"({CAND}/release/). Suite on the final build: {P['SUITE']} passed, 0 failed. Self-checks unchanged (km3 "
            f"81b572198c04d5d1, kx3 31d638dbc818b0fa). Engine source changes since main-c045ede: {len(src_changed)} files "
            f"({P['SRC']}), plus engine/UPSTREAM.md and test files; engine/src/players/, Cargo.lock and Cargo.toml unchanged."),
        'approved': P['APPROVED'],
        'purpose': (
            f"Official engine from {P['PIN']}: main-c045ede's engine (rules switch 2; the kta and km players) plus: the Growl-to-0 "
            f"rule (an attack that an attacker-side effect cuts to 0 does 0, with no Weakness and no defender-side +X; rules/05 "
            f"#11); the hit back an attack leaves (Cursed Jewel, Spike Armor, Bristling Spikes, Needle Lariat, Shell Trap) as "
            f"attack damage in every situation (Dustin, Oct 20; rules/02 section 4): the Attacking Pokemon's lasting cuts and "
            f"prevention apply, and its Rocky Helmet (upstream #367/#418), 20-damage Ability and Poison Barb/Point answer it; "
            f"upstream #385 (on-play 'from your hand onto your Bench' Abilities only on the owner's turn), #390 (random multi-hit "
            f"damage in a fixed order), #401's Fossil part (DiscardFossil offered once) and #344 narrow (Dragon or Colorless "
            f"Energy zones invalid). engine/src/players/ is unchanged: km3 stays the working pilot on both sides of the screen and "
            f"the floor. No new revert switch: the engine reads the same {nsw} DECKGYM_* variables as main-c045ede, none set by "
            f"default; set one and the program is another engine, so never set one in a recorded run. The 0.7.2 RL add-on wheel "
            f"and its run identities are unchanged."),
    }
    m['latest_source_commit'] = F
    m['latest_source_note'] = (f"engine/ is tracked in git. The available release ({NAME}) was built from this commit's engine/; later "
                               f"engine commits are newer source, not the release build.")
    text = json.dumps(m, indent=2, ensure_ascii=False) + '\n'
    json.loads(text)
    files['project_manifest.json'] = text

    files[f'{NEW_DIR}/README.md'] = README.format(**P)

    # ---- START_HERE.md, CLAUDE.md, RUN5 ---------------------------------------------------------------------------
    t = show('START_HERE.md')
    t = once(t, "`rl/engine-2026-10-12/` (`deckgym`, `legality_scan`, `goldfish`), main-c045ede: rules4",
             f"`{NEW_DIR}/` (`deckgym`, `legality_scan`, `goldfish`), {NAME}: rules4", 'START_HERE engine line')
    t = once(t, "; and since Oct 12 rules switch 2: round 2's coin-prevention rules and card-text fixes, Fossils as Item cards, and Weakness on an attack's return damage), with the km pilot",
             f"; since Oct 12 rules switch 2: round 2's coin-prevention rules and card-text fixes, Fossils as Item cards, and Weakness on an attack's return damage; and since {P['PIN_SHORT']} an attack cut to 0 by an attacker-side effect does 0 with no Weakness, an attack's hit back is attack damage for the Attacking Pokémon's own cards (its cuts, its prevention, its Rocky Helmet), plus upstream #385, #390, #401 (Fossil part) and #344 (narrow)), with the km pilot",
             'START_HERE engine line, history')
    files['START_HERE.md'] = t
    t = show('CLAUDE.md')
    t = once(t, CLAUDE_OLD, CLAUDE_NEW.format(**P), 'CLAUDE.md engine paragraph')
    files['CLAUDE.md'] = t
    t = show('rl/RUN5.md')
    t = once(t, RUN5_421_OLD, RUN5_421_NEW.format(**P), 'RUN5 official engine')
    t = once(t, "kt presets replay the Sept 26-28 kt records.\n- **Pilot:** km3 = kta3 + N2",
             "kt presets replay the Sept 26-28 kt records.\n" + RUN5_PINNED.format(**P) + "- **Pilot:** km3 = kta3 + N2", 'RUN5 pinned bullets')
    t = once(t, "`results/floor_recheck_rules2_2026-10/` (planned and committed with the Oct 12 pin; if it fails, the floor isn't used until Dustin has seen the pages).",
             f"`results/floor_recheck_rules2_2026-10/` (planned and committed with the Oct 12 pin; if it fails, the floor isn't used until Dustin has seen the pages); its pages were replayed on {NAME}'s deckgym before the pin ({P['FLOOR_SHORT']}; `results/engine_candidate_2026-10-20/release/`).",
             'RUN5 floor re-check')
    t = once(t, "  - The engine switches of Sept 25, 27, 28 and 30, the rules switch of Oct 1, and rules switch 2 (Oct 11-12).",
             f"  - The engine switches of Sept 25, 27, 28 and 30, the rules switch of Oct 1, rules switch 2 (Oct 11-12), and the Oct 20 engine candidate (pinned {P['PIN_SHORT']}).",
             'RUN5 switches list')
    t = once(t, "on the pinned engine `rl/engine-2026-10-12/` plus a card-effect pass", f"on the pinned engine `{NEW_DIR}/` plus a card-effect pass", 'RUN5 A5')
    files['rl/RUN5.md'] = t

    # ---- rules/ ---------------------------------------------------------------------------------------------------
    for path, pairs in RULES.items():
        t = show(path)
        for i, (old_t, new_t) in enumerate(pairs):
            t = once(t, old_t, new_t.format(**P), f'{path} [{i}]')
        files[path] = t
    t = files['rules/09_engine_repairs_2026-09-22.md']
    t = once(t, "\n## Fixed Oct 12 (rules switch 2, main-c045ede;", "\n" + RULES09_NEW.format(**P) + "\n## Fixed Oct 12 (rules switch 2, main-c045ede;", 'rules/09 Fixed section')
    files['rules/09_engine_repairs_2026-09-22.md'] = t

    # ---- selectors and their tests --------------------------------------------------------------------------------
    p = 'rl/results/ladder_validation/make_predictions.py'
    t = show(p)
    t = once(t, MP_OLD, MP_NEW.format(**P), 'make_predictions CURRENT_ENGINE')
    t = once(t, "def selftest(repo, use_git=True):\n    fails = []\n", MP_SELFTEST, 'make_predictions selftest')
    files[p] = t
    p = 'rl/results/ladder_validation/read_ladder.py'
    t = show(p)
    t = once(t, "def selftest(repo, export, use_git=True):\n    fails = []\n", RL_SELFTEST, 'read_ladder selftest')
    files[p] = t
    p = 'rl/deck_journal/test_journal.py'
    t = show(p)
    t = once(t, "import tempfile\nimport unittest\n", "import tempfile\nimport unittest\nfrom unittest import mock\n", 'test_journal import')
    t = once(t, TJ_OLD, TJ_NEW, 'test_journal replay-B')
    t = once(t, TJ_VIEW_OLD, TJ_VIEW_NEW, 'test_journal deck-01 view')
    files[p] = t

    files[f'{CAND}/RELEASE_NOTES.md'] = NOTES.format(**P, FLOOR_TABLE=V['floor_table'], FLOOR_SORT=V['floor_sort'],
                                                      REPLAY_TABLE=V['replay_table'], SLOWPIN_NOTES=V['slowpin_notes'],
                                                      DRAFT_CHECKS=V['draft_checks'])

    # ---- the commit -----------------------------------------------------------------------------------------------
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
    exists = lambda p: subprocess.run(['git', '-C', REPO, 'cat-file', '-e', f'{base}:{p}'], capture_output=True).returncode == 0
    want_diff = sorted([f'A\t{NEW_DIR}/{n}' for n in ('README.md', 'SHA256SUMS', 'deckgym', 'goldfish', 'legality_scan')] +
                       [('M' if exists(p) else 'A') + f'\t{p}' for p in files if not p.startswith(NEW_DIR)])
    if sorted(diff) != want_diff:
        sys.exit('unexpected tree diff:\n' + '\n'.join(sorted(diff)))
    left = sorted(set(re.findall(r'@@[^@]+@@', ''.join(files.values()))))
    if '--dry-run' in sys.argv:
        print(f'DRY RUN: tree {tree} on base {base[:8]}; {len(diff)} paths:\n' + '\n'.join(diff))
        print('placeholders:', left)
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
    if cur and '--replace' not in sys.argv:
        sys.exit(f'{branch} exists ({cur[:8]}); pass --replace to move it')
    git('update-ref', ref, commit, *([cur] if cur else ['']))
    print(f'draft {commit} on {branch} (parent {base[:8]}, tree {tree[:8]}); {len(diff)} paths:')
    print('\n'.join(diff))
    print(gs('ls-tree', tree, NEW_DIR + '/'))
    print('placeholders left for the adoption:', left)


README = """# The official engine from {PIN_SHORT}: {NAME} (the Growl-to-0 rule, the hit back as attack damage, four upstream fixes)

- **Programs:** `deckgym`, `legality_scan`, `goldfish`; sha256 in `SHA256SUMS` and `project_manifest.json`. Linux (WSL or the cloud). Committed with the executable bit (git mode 100755), so a Linux clone runs them as they are.
  - `deckgym` {DECKGYM_SHA}
  - `legality_scan` {LEGALITY_SCAN_SHA}
  - `goldfish` {GOLDFISH_SHA}
  - These are the programs the final candidate build made and the night's checks ran, copied and never rebuilt (`../../{PD}/`, the same git blobs).
- **Built** in WSL ({BUILT_AT}) from one `git archive` of {F} (branch `laptop/engine-candidate-2026-10-20`), whose `engine/` tree is {FTREE}: `cargo build --release --locked`, `--example legality_scan`, `--example goldfish`, in a fresh folder with an empty target directory, CARGO_BUILD_JOBS 2 (`../results/engine_candidate_2026-10-20/release/build_F.log`). main's `engine/` is that tree, byte for byte.
- **What it is:** main-c045ede's engine (`../engine-2026-10-12/`) plus these changes (`../results/engine_candidate_2026-10-20/PLAN.md`, written before the builds, with its Oct 20 addendum; `rules/09`, "Fixed {PIN_SHORT}"):
  - **The Growl-to-0 rule** (501fc1dd): an attack that an attacker-side effect (Growl, Teary Attack and the like) cuts to 0 does 0: no Weakness, and the Bench hit is cut too, as recorded on Oct 19 (`rules/02` §1, §3; `rules/05` #11). A defender-side "+X damage" effect is skipped as well when the cut reaches 0, and lands when the cut leaves damage, as recorded on Oct 20 (the Luxray/Espathra retry; `rules/05` #11); tests pin both.
  - **The hit back as attack damage** ({ITEM8}; Dustin, Oct 20: "The attack back is treated as an attack in every situation (weakness, attack blocking, bounded field) not like an ability. Abilities don't trigger heavy helmet, attacks do"; `rules/02` §4, `rules/05` #31). The hit back left by Cursed Jewel, Spike Armor, Bristling Spikes, Needle Lariat and Shell Trap keeps its Weakness and Bounded Field and now meets the Attacking Pokémon's own cards: Safeguard, the Bench shields and Disguise prevent it; Intimidating Fang cuts it before Weakness; Heavy Helmet, Steel Apron, Metal Core Barrier and the damage-cut Abilities cut it after Weakness (the recorded Heavy Helmet case: 30 to 10); and when it still damages the Active, that Pokémon's Rocky Helmet (upstream #367, with #418's test), its 20-damage Ability and its Poison Barb or Poison Point answer the holder. Of these, only Weakness, Bounded Field and Heavy Helmet are recorded and only Rocky Helmet is named in the ruling; the rest apply the ruling to each card's text (`../results/engine_candidate_2026-10-20/RELEASE_NOTES.md`, "Readings Dustin can veto").
  - **Upstream #385** (9c51453b): "Once during your turn, when you put this Pokémon from your hand onto your Bench" Abilities (Miraidon ex, Roaring Moon, Poltchageist) are offered only on the owner's turn.
  - **Upstream #390** (75343578): random multi-hit damage is enumerated in a fixed order, so a replay is deterministic.
  - **Upstream #401, the Fossil part** (42d2dd8e): DiscardFossil is offered once, not twice.
  - **Upstream #344, narrow** (764f7459): a deck whose Energy zone holds Dragon or Colorless Energy is invalid, with a named panic.
  - Tests: the ported upstream tests (ccb1d3b5), the "+X" pin and Poltchageist's turn tests ({TESTS}), and the hit back's own ({ITEM8}). `engine/UPSTREAM.md` was refreshed (d9d2e704); its line 9 still says "NOT adopted".
  - {NSRC} source files change. The suite on the final build: {SUITE} passed, 0 failed.
- **Revert switches:** none new. The engine reads the same {NSW} `DECKGYM_*` environment variables as main-c045ede, none set by default. Set one and the program is another engine: never set one in a recorded run. None of the changes above has a switch.
- **What didn't change: the players.** `engine/src/players/`, `Cargo.lock` and `Cargo.toml` are unchanged. km3 stays the working pilot, on both sides of the screen and the floor. The bots still price the hit back flat.
- **Evidence:**
  - The Oct 20 candidate pass (`../results/engine_candidate_2026-10-20/RESULT.md`), on the build of d9d2e704 (the final candidate without the hit back's change): 38 changed games in the old pin's recorded tables, all from the Growl rule (37 in new17 pairing 21, 1 in step 8's km3 carriers; U equals the old pin on each); 1,260 of 12,000 Rayquaza clause-(d) games played old v new, all from #401 (V equals the old pin on all); 0 unexplained.
  - The final build: the floor re-check pages of `../results/floor_recheck_rules2_2026-10/`, {FLOOR_LONG}; and a sample of the candidate pass's runs, {REPLAYS} (`../results/engine_candidate_2026-10-20/release/`).
  - The self-checks are unchanged: km3 81b572198c04d5d1, kx3 31d638dbc818b0fa.
- **Approved:** {APPROVED}. Astra's review (Oct 20, agent mailbox): no implementation defect in the Oct 20 build; adoption after the Growl "+X" choice and the release follow-through.
- **What stays on the old engine:** kx3 and its recorded games, the mixed kt/kta clause-(d) tables (ec7e1a8), scoreboard v3's frozen cells and thresholds and kta3's status, the ladder predictions, exam run 1 and the frozen judge, and the slow report until its re-pin: none is re-run here, none is new-engine evidence, and old thresholds and summaries do not carry over (`../results/engine_candidate_2026-10-20/RELEASE_NOTES.md`).
- **Known limits** (for a later round):
  - The hit back: the coin-flip Abilities on the Attacking Pokémon, Guts and Perish Body, Bouncy Body and Dark Pendant, and who caused a Knock Out (a holder knocked out only by the answering Rocky Helmet counts as knocked out by an attack) are not done; no listed deck reaches them (`rules/09`, open).
  - The "+X" recording covers Intimidating Fang with Lumina Crash's +50 only (Codex's limits: these cards; both tests changed the attacker before the hit; Peculiar Plaza in play).
  - #390's tests compare sorted outcomes; the fixed order rests on the BTreeMap in the code.
  - #344 makes two research deck files invalid (`../results/limitless_skill_model_2026-09-25/decklists/garchomp.txt`, `raticate_ninetales.txt`), and the CLI's message for that rejection is the generic "failed full-deck validation".
  - The recorded kt/kta clause-(d) tables (ec7e1a8) were not replayed; #401 would very likely change them.
- **History:** `../engine-2026-10-12/` (main-c045ede) and earlier are kept unchanged, with their hashes in the manifest's historical releases.
"""

CLAUDE_OLD = """- The official engine program is `rl/engine-2026-10-12/deckgym` (since Oct 12; main-c045ede: rules switch 2,
  round 2's coin-prevention rules on top of main-8626a35, with the card-text fixes, Fossils as Item cards and Weakness
  on an attack's return damage; `engine/src/players/` unchanged; `rl/engine-2026-10-12/README.md`). The working pilot
  is km3, on both sides of the screen and the floor. Since Sept 30, kt3/kta3/ktb3/ktc3 name the kog-based presets
  (kt3, ktb3 and ktc3 are diagnostic only). Earlier programs (`rl/engine-2026-10-02/`, `-09-30/`, `-09-28/`, `-09-27/`,
  `-09-25/`, `rl/addon-0.7.2/deckgym`) are history; the verified add-on 0.7.2 wheel (`rl/addon-0.7.2/wheels/`) is
"""
CLAUDE_NEW = """- The official engine program is `{NEW_DIR}/deckgym` (since {PIN_SHORT}; {NAME}: main-c045ede's engine plus the
  Growl-to-0 rule (an attack cut to 0 by an attacker-side effect does 0, no Weakness), an attack's hit back as attack
  damage for the Attacking Pokémon's own cards, and upstream #385, #390, #401 (Fossil part), #344 (narrow) and #367/#418;
  `engine/src/players/` unchanged; `{NEW_DIR}/README.md`). The working pilot
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
RUN5_421_NEW = ("- **Official engine:** `{NEW_DIR}/`, {NAME} (pinned {PIN_SHORT}; main-c045ede's engine plus the Growl-to-0 rule, an attack's "
                "hit back as attack damage for the Attacking Pokémon's own cards (Dustin, Oct 20), and upstream #385, #390, #401 (Fossil "
                "part), #344 (narrow) and #367/#418; `engine/src/players/` unchanged). Replaying the old pin's recorded games on the Oct 20 "
                "build changed 38, all from the Growl rule (37 in new17 pairing 21, 1 in step 8's km3 carrier rows), and 1,260 of the "
                "12,000 Rayquaza clause-(d) games played old v new, all from #401; 0 unexplained; the final build's floor pages and sample "
                "are in `results/engine_candidate_2026-10-20/release/` ({FLOOR_SHORT}). The pairing-21 and carrier references, scoreboard "
                "v3's frozen cell, kta3's status and km3's thresholds stay main-c045ede's until Dustin decides the re-baselining "
                "(`results/engine_candidate_2026-10-20/RELEASE_NOTES.md`). kt3, ktb3 and ktc3 are kog-based: diagnostic, no identity "
                "claim. Rules switch 2's engine (`rl/engine-2026-10-12/`, main-c045ede; `results/engine_switch_rules2_2026-10/`), the "
                "Oct 2 engine (`rl/engine-2026-10-02/`, main-8626a35),")
RUN5_PINNED = """  - **Pinned {PIN_SHORT}** (`results/engine_candidate_2026-10-20/`: PLAN.md and its Oct 20 addendum, written before the builds; RESULT.md; RELEASE_NOTES.md). Dustin (verbatim): {APPROVED}. Astra's review (Oct 20): no implementation defect in the Oct 20 build; adoption after the Growl "+X" choice and the release follow-through.
    - Not re-run and not new-engine evidence (they stay main-c045ede's; old thresholds and summaries do not carry over): kx3 and its recorded games, the mixed kt/kta clause-(d) tables (ec7e1a8), scoreboard v3's frozen cells and thresholds and kta3's status, the ladder predictions (never overwritten), exam run 1 and the frozen judge.
    - The slow report: {SLOWPIN_RUN5}.
"""

RULES = {
    'rules/02_damage_knockouts_points.md': [
        ("  - **Engine:** it gave 20 for the Active hit until the fix on branch `claude/growl-zero-no-weakness`, not yet pinned; it already cut the Bench hit (`05` #11, `08` T7).",
         "  - **Engine ✓ since {NAME} ({PIN_SHORT}):** 0, no Weakness (it gave 20 for the Active hit before); it already cut the Bench hit (`05` #11, `08` T7). A defender-side \"+X damage\" effect is skipped too when the cut reaches 0, and lands when the cut leaves damage, as recorded on Oct 20 (the next line); tests pin both."),
        ("the Attacking Pokémon's own cards act on it too (its cuts, its prevention, its Rocky Helmet); the engine doesn't do that yet (`09`, open entry).",
         "the Attacking Pokémon's own cards act on it too (its cuts, its prevention, its Rocky Helmet); the engine does since {NAME} ({PIN_SHORT}), except the coin-flip Abilities, Guts and the Knock Out triggers (`09`)."),
        ("⚠ Engine (today's pin, main-c045ede): Weakness and Bounded Field only, no cut, prevention or Rocky Helmet (`09`, open entry)",
         "Engine ✓ since {NAME} ({PIN_SHORT}): Weakness and Bounded Field, then the Attacking Pokémon's lasting cuts, Safeguard, the Bench shields, Disguise and Intimidating Fang, and its Rocky Helmet, 20-damage Ability and Poison Barb/Point answering; not yet: the coin-flip Abilities, Guts, Bouncy Body, Dark Pendant and the Knock Out triggers (`09`, open entry)"),
        ("- **Engine: not yet (planned for the Oct 20 candidate, `laptop/engine-candidate-2026-10-20`).** Today's pin, main-c045ede, gives the hit back Weakness and Bounded Field's ×2 and nothing else: `handle_attack_retaliation` applies it as plain damage, outside `modify_damage` (`engine/src/actions/apply_action_helpers.rs`:774; `09`, open entry).",
         "- **Engine ✓ since {NAME} ({PIN_SHORT}; `09`, \"Fixed {PIN_SHORT}\"):** `handle_attack_retaliation` runs the hit back through `attack_hit_back_damage` (`engine/src/hooks/core.rs`): the Attacking Pokémon's lasting cuts and prevention, then its Rocky Helmet, 20-damage Ability and Poison Barb or Poison Point answer. Before, main-c045ede gave it Weakness and Bounded Field's ×2 only. Not yet: the coin-flip Abilities, Guts, Bouncy Body, Dark Pendant and the Knock Out triggers (`09`, open entry)."),
    ],
    'rules/04_actions_cards_effects.md': [
        ("`02` §4; engine: not yet)", "`02` §4; engine ✓ since {NAME})"),
    ],
    'rules/05_open_questions.md': [
        ("- **Engine:** it gave 20 here. The fix is on branch `claude/growl-zero-no-weakness`, not yet pinned; it is also in the Oct 20 engine candidate (501fc1dd on `laptop/engine-candidate-2026-10-20`), not adopted. The text below is the earlier state of this question.",
         "- **Engine ✓ since {NAME} ({PIN_SHORT}):** 0 here, no Weakness (it gave 20 before; the fix came from branch `claude/growl-zero-no-weakness`, 501fc1dd). The text below is the earlier state of this question."),
        ("- **Engine: not yet (planned for the Oct 20 candidate, `laptop/engine-candidate-2026-10-20`).** Today's pin, main-c045ede, gives the hit back Weakness and Bounded Field only (`09`, open entry).",
         "- **Engine ✓ since {NAME} ({PIN_SHORT})** for the cuts, the prevention and the answers (`09`, \"Fixed {PIN_SHORT}\"); not yet: the coin-flip Abilities, Guts and the Knock Out triggers (`09`, open entry)."),
    ],
    'rules/08_tests_to_record.md': [
        ("The engine gave 20 for the Active hit; the fix is on branch `claude/growl-zero-no-weakness`.",
         "The engine gave 20 for the Active hit; fixed in {NAME} ({PIN_SHORT})."),
        ("Heavy Helmet's cut was already seen (Oct 9). Engine: not yet.",
         "Heavy Helmet's cut was already seen (Oct 9). Engine ✓ since {NAME} ({PIN_SHORT})."),
    ],
    'rules/09_engine_repairs_2026-09-22.md': [
        ("The rule is SETTLED by Dustin's ruling of Oct 20 (below); engine: not yet (planned for the Oct 20 candidate).**",
         "The rule is SETTLED by Dustin's ruling of Oct 20 (below); engine ✓ since {NAME} ({PIN_SHORT}) for the cuts, prevention and answers, still open for the rest (below).**"),
        ("  - **Engine: not yet (planned for the Oct 20 candidate, `laptop/engine-candidate-2026-10-20`).** Today's pin main-c045ede, and the candidate as built (c1670e81), apply the hit back as plain damage plus Weakness (doubled under Bounded Field), `attacker.apply_damage(counter_damage + weakness_extra)` (`engine/src/actions/apply_action_helpers.rs`:795, in `handle_attack_retaliation` at :774), with no cut, prevention or Rocky Helmet. This entry stays under open engine bugs until a pinned engine applies the rule.",
         "  - **Engine ✓ since {NAME} ({PIN_SHORT}; \"Fixed {PIN_SHORT}\" below)** for the Attacking Pokémon's lasting cuts and prevention and its Rocky Helmet, 20-damage Ability and Poison Barb or Poison Point. **Still open** (no listed deck reaches them; `../rl/results/engine_candidate_2026-10-20/PLAN.md`, addendum): the coin-flip Abilities on the Attacking Pokémon (Carefree Steps, Celestial Blessing, Guarded Grill, Securely Sheltered); Guts and Perish Body on an Attacking Pokémon the hit back knocks out; its Bouncy Body and Dark Pendant; and who caused a Knock Out (Lucky Egg, Rescue Scarf, Offload Pass and the Innards Out family on an Attacking Pokémon the hit back knocks out, the holder's Lucky Mittens, and a holder knocked out only by the answering Rocky Helmet or Ability, which counts as knocked out by an attack)."),
    ],
}

RULES09_NEW = """## Fixed {PIN_SHORT} ({NAME}; plan and evidence in `rl/results/engine_candidate_2026-10-20/`; parts of the hit-back entry above stay open)

- **An attack cut to 0 by an attacker-side effect does 0** (501fc1dd, from branch `claude/growl-zero-no-weakness`): no Weakness on the Active, and the Bench hit is cut too, as the Oct 19 recording Growl_weakness_test showed (`02` §1/§3, `05` #11, `08` T7). Before, the engine gave 0 + 20 Weakness. A defender-side "+X damage" effect is skipped as well when the cut reaches 0, and lands when the cut leaves damage, as recorded on Oct 20 (the Luxray/Espathra retry, `05` #11); `a_defender_side_plus_x_is_also_skipped_when_the_cut_reaches_zero` and `a_defender_side_plus_x_lands_when_the_cut_leaves_damage_and_not_at_zero` (`engine/src/hooks/core.rs`) pin it.
- **The hit back an attack leaves is attack damage in every situation** ({ITEM8}; Dustin, Oct 20, `02` §4, `05` #31): `attack_hit_back_damage` (`engine/src/hooks/core.rs`), called from `handle_attack_retaliation`, applies the Attacking Pokémon's prevention (Safeguard against a Pokémon ex holder, Protective Poncho and Shell Shield on the Bench, then Disguise), its side's Intimidating Fang before Weakness, Weakness and Bounded Field as before, and its lasting cuts after Weakness (Heavy Helmet, Steel Apron, Metal Core Barrier, the "-X damage from attacks" Abilities, Thick Fat, Resilience Link, Ice Face, GUARD, Coordinated Unit). When it still damages the Active, the Attacking Pokémon's Rocky Helmet (upstream #367; #418's test ported), its 20-damage Ability and its Poison Barb or Poison Point answer the holder; never its own new hit back. Effects stored on it this turn and its side's turn effects are not read (they cover the opponent's next turn). The recorded case: Heavy Helmet cuts Bristling Spikes' hit back from 30 to 10 (20261009_223237000). Tests: `engine/tests/rules_repair_hit_back_attack_damage.rs`, `engine/tests/tools/rocky_helmet_delayed_counterattack_test.rs` and `hooks/core.rs`'s `attack_cut_to_zero_and_hit_back_tests`.
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
    "label": "{NAME} (Growl-to-0, the hit back as attack damage, upstream fixes; pinned {PIN_SHORT})",
    "harness_engine_trees": [],                         # slow reports / exams: "engine tree <12 hex>" in manifest.json (none until the slow report's re-pin)
    "floor_engines": ["{NEW_DIR}/deckgym"],  # floor pages: "- Engine: <path>"
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

NOTES = """# Release notes: {NAME}, the final engine candidate (DRAFT: not adopted)

**Not adopted.** This file comes with the adoption draft on `laptop/engine-adoption-draft-2026-10-20`; main is untouched by it, and the adoption waits for Dustin's yes. His open calls: #385 as a rule, the re-baselining (item 3 below), the readings of his Oct 20 ruling listed next (he can veto each), and the holder-side boosts on a hit back (not named in the ruling). The Growl rule's "+X" case is recorded (Oct 20, the Luxray/Espathra retry), and the candidate matches it.

## Readings Dustin can veto: his Oct 20 ruling applied to card text, not recorded
His words: "The attack back is treated as an attack in every situation (weakness, attack blocking, bounded field) not like an ability. Abilities don't trigger heavy helmet, attacks do". Of the hit back's interactions, only Weakness (183108), Bounded Field (Boundedfield_hitback_test) and Heavy Helmet's cut (20261009_223237000) are recorded, and Rocky Helmet is the card the ruling names. These two follow from the ruling and each card's text and were never seen in a game:
1. **The Rough Skin-type Abilities answer a hit back.** Rough Skin, Counterattack, Steel Spikes and Automated Combat read "If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon"; the hit back counts as damage from an attack, so the Attacking Pokémon's Ability answers the holder with 20 (an Ability's damage, which ends the chain; tests pin both).
2. **Intimidating Fang cuts a hit back.** "As long as this Pokémon is in the Active Spot, attacks used by your opponent's Active Pokémon do −20 damage": the hit back is treated as the holder's attack, so a Luxray hit back takes 20 less, before Weakness, and a hit back cut to 0 does nothing.
On the same footing, with less at stake: Poison Barb and Poison Point poisoning the holder; Safeguard, Disguise and the Bench shields preventing it; the damage-cut Abilities and Tools other than Heavy Helmet. No listed deck reaches any of these except Rocky Helmet (t-blaziken) and Shuckle ex's Solid Shell (t-vespiquen) against brews 07 and 09. Each can be taken out with a small code change.

## What the adoption activates
- **The three programs** in `{NEW_DIR}/` (`deckgym` {DECKGYM_BLOB}… blob, sha256 {DECKGYM_SHA}; `legality_scan` {LEGALITY_SCAN_SHA}; `goldfish` {GOLDFISH_SHA}): the final build's tested bytes, the same git blobs as `{PD}/`, mode 100755, never rebuilt.
- **The current-engine selector.** `project_manifest.json`'s `available_release` names them. `current_engine.py`, `decks/screen/floor.py` and `decks/screen/run_screen.py` read it, so the screen and the floor switch with the manifest. `make_predictions.py`'s `CURRENT_ENGINE` moves with it: floor pages made on `{NEW_DIR}/deckgym` count as current, and no slow report does until the slow report's re-pin.
- **The slow-report program:** {SLOWPIN_NOTES}

## Release identity
- Built from {F} ({BUILT_AT}); engine tree {FTREE}. main's `engine/` after the adoption is that tree, byte for byte: no exception.
- The Oct 20 build (d9d2e704, deckgym 245e11e8…) is the final candidate without the hit back's change; it carried the Oct 20 pass and is the attribution build below.
- **Activation checks** (after the merge, in the repository root, on Linux):
  1. `cd {NEW_DIR} && sha256sum -c SHA256SUMS`: three OK lines.
  2. `git ls-tree HEAD {NEW_DIR}/`: deckgym {DECKGYM_BLOB}…, legality_scan {LEGALITY_SCAN_BLOB}…, goldfish {GOLDFISH_BLOB}…, each 100755.
  3. `python3 current_engine.py`: prints this repository's `{NEW_DIR}/deckgym` (it refuses a file whose hash is not the manifest's).
  4. The manifest's three sha256 equal `SHA256SUMS`.

## The floor re-check pages on the final build
{FLOOR_TABLE}

{FLOOR_SORT}

## A sample of the Oct 20 pass's runs, replayed on the final build
{REPLAY_TABLE}

## Tied to the OLD engine (main-c045ede): not re-run, and not new-engine evidence
Old thresholds and summaries do not carry over. Each item stays a record of main-c045ede (or of an older engine):
1. **kx3 and its recorded games.** The slow-report pin (program 76df495b; laptop/kx3-on-rules2 cd20a97a, engine tree 4ebb30a9) until its re-pin; the 8 slow reports made on it (`rl/results/slow_reports/2026-10-12_*`, `2026-10-13_*`, `2026-10-14_*`; brews 07 and 09's rows against t-blaziken and t-vespiquen are among those the hit back's change can move) and the paired dry runs; `kx3_on_rules2_2026-10/` (its 202 + 202 replay games), `m64_on_rules2_2026-10/` and `pause_positions_kx3_2026-10/`. kx3's unchanged self-check digest is a 12-game check, not identity for those games.
2. **The mixed kt/kta clause-(d) tables (ec7e1a8):** `kt_tables_2026-09-28/ec7e1a8_d_*` and `ec7e1a8_mixed_*`, `kta_tables_2026-09-29/ec7e1a8_fresh_d_*` and `ec7e1a8_fresh_id_*_d_i20`. Not replayed. On the same deals #401 changed 15.7% of km3's and 15.5% of kta3's Rayquaza games, so these would very likely change.
3. **Scoreboard v3's frozen cells and thresholds, and kta3's status.** `scoreboard_v3_2026-09-27/frozen_cells.csv` (its altaria_greninja v hydreigon cell holds new17 pairing 21, where k3 changes 8 and kp3 7 of 500 games), RUN5's development real error (k3 15.3, kp3 15.5, kog3 14.0), kta3's "adopted, unconfirmed" status and km3's Stadium thresholds (`km_tables_2026-09-30/READING.md`). The re-baselining is Dustin's decision (the precedent is switch 2's PLAN, question 3a). The would-be new references are the candidate's 7 game files in `games/new/`; their names keep the `08a9b3a_` prefix of the commands they replay, but the candidate played them.
4. **The ladder predictions** (`rl/results/ladder_validation/predictions/`, 8 files), never overwritten. After the pin `read_ladder.py` prints "NOT the current engine now" for them; new-engine predictions are new files, from new-engine pages and reports. Brews 07 and 09's predictions are built from rows the hit back's change can move.
5. **Exam run 1 and the frozen AI judge** (frozen-4, engine 70652fff; `weekly_review_2026-10-18/RUN1_OUTCOME.md`). A later run on this engine needs a new freeze (frozen-5).
6. **The Oct 12 floor re-check pages** (`floor_recheck_rules2_2026-10/`) and their runners. The final build's pages above are new records beside them, never replacements.
7. **Also on the old engine:** the deck journal's stored "current engine" flags (deck 01's two kx3/km3 entries mean "current when added"); the pg_pos position harnesses and the pause-game position lists (`next_pilot_2026-10/old_positions/`, `pause_games_new_2026-10-12/` and `-13/`; five positions from game 261005_183108000 hold Mega Sableye ex and Poison Barb at the list level); the setup tester's runs (labelled c045ede; probably unaffected, not checked); dated prose naming main-c045ede or `rl/engine-2026-10-12/` (history, left as is). One of those can mislead a reader: `deck_improvement/kingambit_2026-10-15/CHECK.md:359` says to use `rl/engine-2026-10-12/deckgym`.

What carries over unchanged: every replayed row that came out equal.

## Checks of the draft (a scratch worktree; no engine run)
{DRAFT_CHECKS}

## Left as is on purpose
- `engine/UPSTREAM.md` line 9 still says "NOT adopted". RUN5, this file and `{NEW_DIR}/README.md` record the adoption.
- The Oct 20 build's programs (`programs/`), the U and V builds (local refs, not pushed) and the laptop's `pincand_work` stay until the adoption is decided.
"""

COMMIT_MSG = """DRAFT, NOT ADOPTED: pin the final engine candidate as {NAME} ({NEW_DIR}/)

The adoption commit, drafted for Dustin's yes; not on main, not to be merged without it. The @@...@@
placeholders (the pin date and his words) are filled by re-running the generator at adoption
(rl/results/engine_candidate_2026-10-20/release/tools/adopt_final.py). Parent {BASE}.

- {NEW_DIR}/: the final build's tested programs (deckgym {DECKGYM_SHA}, the same blobs as
  {PD}/, mode 100755), SHA256SUMS, README.md.
- project_manifest.json: main-c045ede moves to historical_releases (superseded); available_release is
  {NAME} (source_commit {F8}, the built commit; main's engine/ is its tree); latest_source_*.
- START_HERE.md and CLAUDE.md pin lines, rl/RUN5.md, rules/02, 04, 05, 08, 09 (engine status lines; a
  "Fixed" section).
- make_predictions.py CURRENT_ENGINE moves (no slow-report tree until the re-pin); its deck-12 self-test
  and read_ladder.py's run under the Oct 12 value; test_journal's two REPLAY_B tests add it under the Oct 12 value.

Release notes, in this commit: rl/results/engine_candidate_2026-10-20/RELEASE_NOTES.md.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
"""

if __name__ == '__main__':
    main()
