#!/usr/bin/env python3
"""Pre-registration for a strength run: writes the manifest the program executes and PREREGISTRATION.md, before any game is played.

  strength_prereg.py --config CONFIG.json --out RUNDIR [--repo ROOT]

CONFIG.json (all keys but the first four optional):
  name, question          what this run is for, in a sentence
  pilot, reference        pilot specs: an engine pilot code (km3, kog3, ...) or `ext:<command>` for an external process
  deck_groups, decks      decks under test: group names from groups.json, and/or single deck names from decks.json
  deck_files              decks under test given by file path inside the repository (name = the file's stem), for a list that is not in decks.json
  opponent_groups, opponents   the opponent pool, the same way (default: the same as the decks under test)
  deals (default 200; below pair_stride), seats ([0, 1]), seed_base, pair_stride (10000), threads (2), log_level (deck | full | none), ext_timeout_s
  stage                   dev (default), heldout or use. A held-out deck is refused unless stage is heldout AND heldout.json says locked: false.
                          `use` (the slow report): allowed on any deck, recorded as `use`, never development evidence; it does not touch the lock
                          (the manifest lists no held-out names for the program's own guard, and keeps them under heldout_registry / heldout_in_run)
  intended_lines          path of the intended-lines file (default rl/strength/intended_lines.json)
  program, program_sha256, engine, pilot_provenance, reference_provenance   free text recorded as given (build.sh prints them)
  selfcheck_given         {pilot spec: self-check text}: recorded instead of playing the 12 self-check games. Only at stage `use`; only with a program file whose
                          sha256 was verified against program_sha256; and only when selfcheck_given_program_sha256 (the sha256 of the binary the text was
                          measured on: the pin's, or the program's own for a text replayed just now) equals that program's sha256, because a digest belongs to
                          the exact binary it was measured on. selfcheck_how 'replayed' makes the recorded source say the text was replayed on the registering machine
                          (otherwise: copied from the pin). A spec not named here is still checked.
                          A given text is held to the committed pin: the pin that the slow_report block names (path and sha256) must be the
                          rl/strength/slow_report_pin.json committed at HEAD of --repo (only the test-only variable SLOW_REPORT_ALLOW_UNCOMMITTED_PIN lets the
                          file with that sha256 through), every given text must be the pin's own text for that pilot, and a copied (not replayed) text must be
                          one the pin says was measured on this program (selfcheck_measured_on_sha256). The block's pin_committed is what the script found
                          ('yes' or 'bypassed'); a config that says another state is refused. The same pin is asked for whenever the block carries a
                          pin_committed or a program_route, text or no text; a program_route is checked against a program that is there ('pinned': the
                          pin's program; 'rebuilt': PROGRAM.build.json on disk is for this program and the pin's engine tree and harness source, and the
                          block's build_record is that file's), and a text said to be replayed (selfcheck_how) needs such a route.
  selfcheck_given_program_sha256, selfcheck_how   see selfcheck_given
  slow_report             a free block recorded in the manifest and named in PREREGISTRATION.md (written by slow_report.py)

Refuses to write into a run directory that already holds games. The manifest's sha256 is written beside it and into the README; the report
checks that the manifest still matches.
"""
import argparse, collections, hashlib, json, os, re, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# variables that make git read ANOTHER repository whatever `git -C` says (a git hook or `rebase --exec` exports them); slow_report.py reads its git with them removed too
GIT_REPO_VARS = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_COMMON_DIR', 'GIT_NAMESPACE', 'GIT_PREFIX')
PIN_REL = 'rl/strength/slow_report_pin.json'
ALLOW_UNCOMMITTED_PIN = 'SLOW_REPORT_ALLOW_UNCOMMITTED_PIN'  # test only (see slow_report.py): lets a hand-made pin through, and the registration says so
STAGES = ('dev', 'heldout', 'use')
_WHITE_SPACE_RUN = re.compile('[\\t\\n\\x0b\\x0c\\r \\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000]+')  # Rust's char::is_whitespace (Unicode White_Space), as the engine splits a line


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def deck_signature(path):
    """What the engine reads from a deck file, not how it was saved: the cards by id (set and number, the number padded to three digits as the engine does),
    counts merged per card, hashed. The engine (engine/src/deck.rs) ignores the printed name and takes the last two words of a line as the id, so an ASCII-folded or
    otherwise respelled copy of a held-out deck, a CRLF or BOM copy, another line order, extra spaces or other Unicode white space, split counts, `Pokémon:` /
    `Trainer:` heading lines and an unpadded number all have the same signature as the original (test_strength_prereg_use.py). The Energy line is left out on
    purpose: with no Energy line the engine derives the Energy types from the cards, so the same 20 cards are the same deck for this guard, which refuses
    near-copies rather than missing them. A file the engine cannot read as a deck falls back to its raw bytes; one that cannot be opened raises OSError."""
    try:
        with open(path, 'rb') as f:
            text = f.read().decode('utf-8-sig')
        cards = collections.Counter()
        for ln in text.split('\n'):
            words = [w for w in _WHITE_SPACE_RUN.split(ln) if w]
            if not words or words[0].startswith(('Pokémon:', 'Trainer:', 'Energy:')):
                continue
            if len(words) < 3:
                raise ValueError('not a card line')
            n = int(words[0])
            if n:
                cards[f'{words[-2].lower()} {words[-1].zfill(3)}'] += n
        if not cards:
            raise ValueError('no cards')
        return hashlib.sha256(json.dumps(sorted(cards.items())).encode('utf-8')).hexdigest()
    except Exception:
        return 'raw:' + sha(path)


def committed_pin(root, sr):
    """(the pin, 'yes' | 'bypassed') for a `use` config that gives a self-check text: the pin the slow-report block names (by its sha256) must be the rl/strength/slow_report_pin.json
    committed at HEAD of the repository `root` (git read without GIT_DIR and its relatives), or, only with the test-only variable SLOW_REPORT_ALLOW_UNCOMMITTED_PIN, the file the
    block's path names with that sha256 ('bypassed'). A text 'copied from the pin' or 'replayed and equal to the pin' means something only against the committed pin: a config written
    by hand and run through this script directly must not be able to claim it. Exits with a REFUSED message (before anything is written) otherwise."""
    entry = (sr or {}).get('pin') if isinstance((sr or {}).get('pin'), dict) else {}
    want, rel = entry.get('sha256'), entry.get('path')
    env = {k: v for k, v in os.environ.items() if k not in GIT_REPO_VARS}
    env['GIT_OPTIONAL_LOCKS'] = '0'
    why = ''
    try:
        r = subprocess.run(['git', '-C', root, 'cat-file', 'blob', f'HEAD:./{PIN_REL}'], capture_output=True, env=env)
        if r.returncode != 0:
            said = r.stderr.decode('utf-8', 'replace').strip()
            why = f'HEAD has no {PIN_REL} in {root}' + (f' (git said: {said.splitlines()[0][:200]})' if said else '')
        elif not isinstance(want, str) or hashlib.sha256(r.stdout).hexdigest() != want:
            why = f'the pin the config names (sha256 {str(want)[:12]}) is not the {PIN_REL} committed at HEAD (sha256 {hashlib.sha256(r.stdout).hexdigest()[:12]})'
        else:
            try:
                return json.loads(r.stdout.decode('utf-8')), 'yes'
            except ValueError as e:
                why = f'the {PIN_REL} committed at HEAD cannot be read ({e})'
    except OSError:
        why = 'git is not available, so the committed pin cannot be read'
    if os.environ.get(ALLOW_UNCOMMITTED_PIN) and isinstance(want, str) and isinstance(rel, str) and rel:
        for p in ([rel] if os.path.isabs(rel) else [os.path.join(root, rel), os.path.join(HERE, '..', '..', rel)]):
            if os.path.isfile(p) and sha(p) == want:
                try:
                    return load_json_file(p), 'bypassed'
                except (OSError, ValueError) as e:
                    why += f'; {p} cannot be read ({e})'
        why += f'; no pin file with sha256 {want[:12]} at {rel} either (allowed by {ALLOW_UNCOMMITTED_PIN}, test use)'
    sys.exit(f'REFUSED: the pin the config names is not the committed one: {why}. A given self-check text is the pin\'s own, so the pin must be the {PIN_REL} committed at HEAD of the repository '
             '(commit it, or leave the text out and let the script play the self-check). Nothing was written.')


def route_problem(route, prog, prog_sha, pin, block):
    """None, or why the program at `prog` does not fit the route the slow_report block names. 'pinned': it is the pin's program (sha256). 'rebuilt': its build record, PROG.build.json, is
    on disk and is for this program (schema 1, its sha256) and the pin's engine tree and harness source, and the record the block carries is that file's (its sha256 and the same entries).
    This is what stands behind 'a rebuild of the pinned source' on the page: a hand-written block can no longer say it without the file."""
    if route == 'pinned':
        if prog_sha != pin.get('program_sha256'):
            return (f'the config says the program is the pinned binary (route pinned), but the program at {prog} has sha256 {str(prog_sha)[:12]} and the pin\'s program has '
                    f'{str(pin.get("program_sha256"))[:12]}')
        return None
    path = prog + '.build.json'
    if not os.path.isfile(path):
        return f'the config says the program is a rebuild (route rebuilt), but {path} is not there: the build record that build.sh writes beside a program is what a rebuild is checked by'
    try:
        rec = load_json_file(path)
    except (OSError, ValueError) as e:
        return f'the build record {path} cannot be read ({e})'
    if not isinstance(rec, dict):
        return f'the build record {path} cannot be read (it is not an object)'
    diffs = []
    if type(rec.get('schema')) is not int or rec['schema'] != 1:
        diffs.append(f'schema {rec.get("schema")}, not 1')
    if rec.get('program_sha256') != prog_sha:
        diffs.append(f'program_sha256 {str(rec.get("program_sha256"))[:12]}, not {str(prog_sha)[:12]}')
    for key in ('engine_tree_archived', 'harness_source_sha256'):
        want = pin.get('engine_tree' if key == 'engine_tree_archived' else key)
        if not want or rec.get(key) != want:
            diffs.append(f'{key} {str(rec.get(key))[:12]}, not the pin\'s {str(want)[:12]}')
    if diffs:
        return f'the build record {path} is not for this program and the pinned source ({"; ".join(diffs)})'
    held = block.get('build_record')
    if not isinstance(held, dict):
        return 'the block carries no build record, and so cannot say which one the rebuild has'
    if held.get('record_sha256') != sha(path) or any(held.get(k) != rec.get(k) for k in ('program_sha256', 'engine_tree_archived', 'harness_source_sha256')):
        return f'the build record in the block is not the one at {path}'
    return None


def load_json_file(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--repo', default=os.path.abspath(os.path.join(HERE, '..', '..')))
    a = ap.parse_args()
    def load(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    cfg = load(a.config)
    root = a.repo
    reg = load(os.path.join(HERE, 'decks.json'))['decks']
    groups = load(os.path.join(HERE, 'groups.json'))
    held = load(os.path.join(HERE, 'heldout.json'))
    held_names = list(held.get('decks', []))
    stage = cfg.get('stage', 'dev')
    if stage not in STAGES:
        sys.exit(f'unknown stage {stage!r}: the stages are {", ".join(STAGES)}')
    if stage == 'use':
        sr = cfg.get('slow_report')
        if not (isinstance(sr, dict) and sr.get('headline') and sr.get('pin')):
            sys.exit('REFUSED: stage `use` is only for the slow report (rl/strength/slow_report.py): the config must carry its `slow_report` block, with a headline and the pin it was made under')

    # decks given by file path: really inside the repository (a symlink is followed), named by the file's stem, hashed like a registered deck
    reg = dict(reg)
    root_abs = os.path.abspath(root)
    root_real = os.path.realpath(root_abs)
    given_decks = []
    for p in cfg.get('deck_files') or []:
        abs_p = os.path.abspath(os.path.join(root_abs, p))
        if os.path.commonpath([os.path.realpath(abs_p), root_real]) != root_real:
            sys.exit(f'deck file {p} is not inside the repository ({root_abs}): the run hashes and records its decks at a commit, so copy the file into the repository first')
        if os.path.isdir(abs_p):
            sys.exit(f'deck file {p} is not a file (it is a directory)')
        if not os.path.isfile(abs_p):
            sys.exit(f'deck file {p} not found (looked for {abs_p})')
        rel = os.path.relpath(abs_p, root_abs).replace(os.sep, '/')
        already = [n for n, q in reg.items() if os.path.normpath(q) == os.path.normpath(rel)]
        name = already[0] if already else os.path.splitext(os.path.basename(rel))[0]  # a file that is already registered keeps its registered name
        if name in reg and os.path.normpath(reg[name]) != os.path.normpath(rel):
            sys.exit(f'deck file {rel} is named {name!r}, which is already a different registered deck ({reg[name]}); rename the file')
        reg[name] = rel
        if name not in [g['name'] for g in given_decks]:
            given_decks.append(dict(name=name, path=rel))

    def expand(group_names, names):
        out = []
        for g in group_names or []:
            if g not in groups or g.startswith('_'):
                sys.exit(f'unknown group {g!r}')
            out += groups[g]
        out += names or []
        seen, res = set(), []
        for n in out:
            if n not in reg:
                sys.exit(f'deck {n!r} is not in decks.json')
            if n not in seen:
                seen.add(n)
                res.append(n)
        return res

    decks = expand(cfg.get('deck_groups'), (cfg.get('decks') or []) + [g['name'] for g in given_decks])
    if not decks:
        sys.exit('no decks under test (deck_groups / decks / deck_files)')
    opps = expand(cfg.get('opponent_groups'), cfg.get('opponents')) if (cfg.get('opponent_groups') or cfg.get('opponents')) else list(decks)
    # the held-out guard, by name and by what the file says (the cards, not the bytes, so a renamed or re-exported copy does not slip through). A `use`
    # run is not development, so it is allowed on any deck; it is recorded as such and does not lift the lock.
    def signature_of(n):
        try:
            return deck_signature(os.path.join(root, reg[n]))
        except OSError as e:
            sys.exit(f'REFUSED: the deck file of {n} ({reg[n]}) cannot be read ({e.strerror or e}), so the held-out guard cannot compare it; nothing was written.')
    held_sigs = {signature_of(n): n for n in held_names if n in reg}
    held_in_run = []
    for n in decks + opps:
        if n in held_names or signature_of(n) in held_sigs:
            if n not in held_in_run:
                held_in_run.append(n)
            if stage != 'use' and (stage != 'heldout' or held.get('locked', True)):
                sys.exit(f'REFUSED: {n} is a held-out deck. A development run never uses it; it is unlocked only when heldout.json says locked: false and the run says stage: heldout.')
    if stage == 'heldout' and held.get('locked', True):
        sys.exit('REFUSED: stage heldout, but heldout.json is still locked.')

    deals = int(cfg.get('deals', 200))
    seats = cfg.get('seats', [0, 1])
    stride = int(cfg.get('pair_stride', 10000))
    if deals > stride:
        sys.exit(f'deals ({deals}) must not exceed pair_stride ({stride}), or the seeds of neighbouring pairs overlap')
    # the program and the self-check text it may be given are validated before anything is created: a refusal leaves no run directory behind
    prog = cfg.get('program')
    prog_sha = cfg.get('program_sha256')
    if prog and os.path.isfile(prog):
        actual = sha(prog)
        if prog_sha and prog_sha != actual:
            sys.exit(f'program_sha256 in the config ({prog_sha[:12]}) is not the program at {prog} ({actual[:12]})')
        prog_sha = actual
    given = cfg.get('selfcheck_given') or {}
    if given and stage != 'use':
        sys.exit('REFUSED: selfcheck_given is only for stage use (the slow report, which pins one frozen build); a development or held-out run replays its own self-check')
    if given and not (isinstance(given, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in given.items())):
        sys.exit('selfcheck_given must be a mapping of pilot spec to self-check text')
    if given and not (cfg.get('program_sha256') and prog and os.path.isfile(prog)):
        sys.exit('selfcheck_given is only accepted with a program file and its program_sha256 in the config (the digest belongs to that exact binary, and its sha256 is checked)')
    if given and cfg.get('selfcheck_given_program_sha256') != prog_sha:
        sys.exit(f'REFUSED: the self-check text was measured on a program with sha256 {str(cfg.get("selfcheck_given_program_sha256"))[:12]}, but the program at {prog} has sha256 '
                 f'{str(prog_sha)[:12]}: a digest belongs to the exact binary it was measured on, so the text cannot be recorded for this one (replay the self-check on it instead)')
    block = cfg.get('slow_report') if stage == 'use' else None
    if block and (given or block.get('pin_committed') is not None or block.get('program_route') is not None):
        # a given text, a pin state and a program route are claims about the pin: held to the committed pin, so that no config can claim pinned provenance for a text, a state or a
        # program the pin does not have (slow_report.py's own configs always pass this)
        pin, pin_state = committed_pin(root, block)
        claimed = block.get('pin_committed')
        if claimed is not None and claimed != pin_state:
            sys.exit(f'REFUSED: the config says the pin is {claimed!r} but strength_prereg.py finds it is {pin_state!r}. Nothing was written.')
        block['pin_committed'] = pin_state  # what this script found, whatever the config said (or left out)
        route = block.get('program_route')
        if given and cfg.get('selfcheck_how') == 'replayed' and route not in ('pinned', 'rebuilt'):
            sys.exit('REFUSED: a replayed self-check text needs a program route (pinned or rebuilt) in the slow_report block, so that what it was replayed on can be checked. Nothing was written.')
        if route in ('pinned', 'rebuilt') and prog and os.path.isfile(prog):
            problem = route_problem(route, prog, prog_sha, pin, block)
            if problem:
                sys.exit(f'REFUSED: {problem}. Nothing was written.')
        for spec, text in given.items():
            pin_text = (pin.get('selfcheck') or {}).get(spec) if isinstance(pin.get('selfcheck'), dict) else None
            if pin_text != text:
                sys.exit(f'REFUSED: the self-check text given for {spec} is not the text the pin has for it (given: {text}; pin: {pin_text if pin_text is not None else "none"}): '
                         'a text that is not the pin\'s cannot be recorded as the pin\'s. Nothing was written.')
        if given and cfg.get('selfcheck_how') != 'replayed':  # a replayed text is a rebuild's own (slow_report.py checked it equals the pin's); a copied one belongs to the pinned binary
            measured_on = pin.get('selfcheck_measured_on_sha256')
            if not measured_on:
                sys.exit(f'REFUSED: the pin does not say which program its self-check texts were measured on, so they cannot be copied for the program at {prog} (a rebuild replays the self-checks instead). '
                         'Nothing was written.')
            if cfg.get('selfcheck_given_program_sha256') != measured_on or prog_sha != measured_on:
                sys.exit(f'REFUSED: the pin says its self-check texts were measured on a program with sha256 {str(measured_on)[:12]}, but this config copies them for the program at {prog} '
                         f'(sha256 {str(prog_sha)[:12]}): a copied text belongs to the binary it was measured on (a rebuild replays the self-checks instead). Nothing was written.')
    os.makedirs(a.out, exist_ok=True)
    if os.path.exists(os.path.join(a.out, 'games.jsonl')):
        sys.exit('this run directory already holds games; pre-registration comes first')
    seed_base = int(cfg.get('seed_base', 24_300_000_000))
    pairs = [(d, o) for d in decks for o in opps if d != o]
    games = len(pairs) * deals * len(seats) * 2
    lines_path = cfg.get('intended_lines', 'rl/strength/intended_lines.json')
    lines_abs = os.path.join(root, lines_path) if not os.path.isabs(lines_path) else lines_path
    lines_sha = sha(lines_abs) if os.path.exists(lines_abs) else None
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # provenance: the program's own hash, the repository commit, and a digest of 12 fixed games for each engine pilot (two builds that play
    # the same reference pilot must print the same digest)
    try:
        git_env = {k: v for k, v in os.environ.items() if k not in GIT_REPO_VARS}  # the checkout we were told about, not a repository named by an exported GIT_DIR (a git hook, rebase --exec)
        repo_commit = subprocess.run(['git', '-C', root, 'rev-parse', 'HEAD'], capture_output=True, text=True, env=git_env).stdout.strip() or None
    except Exception:
        repo_commit = None
    selfcheck, selfcheck_source = {}, {}
    # only a pin recorded as committed is called the committed pin: a state that is missing is not "yes" (a given text always has it, found above)
    pin_phrase = 'the committed pin' if (cfg.get('slow_report') or {}).get('pin_committed') == 'yes' else 'the pin file in use, which is NOT the committed pin: test use'
    given_source = (f'replayed by slow_report.py on the registering machine just before registration (equal to {pin_phrase})' if cfg.get('selfcheck_how') == 'replayed'
                    else 'given in the config (copied from the pin, which says it was measured on this exact program sha256)')
    if prog and os.path.isfile(prog):
        da, db = reg.get('t-altaria'), reg.get('t-suicune')
        for spec in sorted({cfg['pilot'], cfg['reference']}):
            if spec in given:
                selfcheck[spec] = given[spec]
                selfcheck_source[spec] = given_source
                continue
            if spec.startswith('ext:') or not da or not db:
                continue
            r = subprocess.run([prog, 'selfcheck', '--root', root, '--pilot', spec, '--deck-a', da, '--deck-b', db, '--games', '12'], capture_output=True, text=True)
            selfcheck[spec] = r.stdout.strip() or ('failed: ' + r.stderr.strip()[-200:])
            selfcheck_source[spec] = 'run by strength_prereg.py'

    manifest = {
        'name': cfg.get('name', os.path.basename(os.path.normpath(a.out))), 'question': cfg.get('question', ''),
        'repo_commit': repo_commit, 'selfcheck': selfcheck, 'selfcheck_source': selfcheck_source,
        'created_at': now, 'stage': stage, 'repo_root': root,
        'pilot': cfg['pilot'], 'reference': cfg['reference'],
        'decks': [{'name': n, 'path': reg[n], 'sha256': sha(os.path.join(root, reg[n]))} for n in decks],
        'opponents': [{'name': n, 'path': reg[n], 'sha256': sha(os.path.join(root, reg[n]))} for n in opps],
        'deals': deals, 'seats': seats, 'seed_base': seed_base, 'pair_stride': stride, 'threads': int(cfg.get('threads', 2)),
        'log_level': cfg.get('log_level', 'deck'), 'ext_timeout_s': cfg.get('ext_timeout_s'),
        # what the program's own guard reads: a `use` run lists no held-out names there (it is not development), the others list them all
        'heldout_decks': [] if stage == 'use' else held_names, 'heldout_locked': held.get('locked', True),
        'heldout_registry': held_names, 'heldout_in_run': held_in_run,
        'intended_lines': lines_path, 'intended_lines_sha256': lines_sha,
        'program': cfg.get('program'), 'program_sha256': prog_sha, 'engine': cfg.get('engine'),
        'pilot_provenance': cfg.get('pilot_provenance'), 'reference_provenance': cfg.get('reference_provenance'),
        'planned_pairs': len(pairs), 'planned_games': games,
    }
    if given_decks:
        manifest['deck_files'] = given_decks
    if cfg.get('slow_report'):
        manifest['slow_report'] = cfg['slow_report']
    mpath = os.path.join(a.out, 'manifest.json')
    if os.path.exists(mpath):
        sys.exit('manifest.json already exists in this run directory; pre-registration is written once (use a new directory)')
    with open(mpath, 'w', encoding='utf-8') as f:
        f.write(json.dumps(manifest, indent=1, ensure_ascii=False))
    msha = sha(mpath)  # manifest.sha256 is written last, after PREREGISTRATION.md: a folder without it is an unfinished registration (slow_report.py clears it)

    L = []
    L.append(f"# Pre-registration: {manifest['name']}\n")
    L.append(f"Written {now}, **before any game was played**. The manifest (`manifest.json`, sha256 `{msha}`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.\n")
    L.append('## Question\n')
    L.append((cfg.get('question') or '(none given)') + '\n')
    L.append('## Pilots\n')
    L.append(f"- **Pilot under test (arm X):** `{cfg['pilot']}`" + (f" ({cfg['pilot_provenance']})" if cfg.get('pilot_provenance') else ''))
    L.append(f"- **Reference (arm ref, and the opponent in both arms):** `{cfg['reference']}`" + (f" ({cfg['reference_provenance']})" if cfg.get('reference_provenance') else ''))
    L.append(f"- Program: `{cfg.get('program')}` sha256 `{prog_sha}`; engine: {cfg.get('engine')}; repository commit: `{repo_commit}`")
    for spec, txt in selfcheck.items():
        src = selfcheck_source.get(spec, '')
        how = (' (given in the config, copied from the pin and not replayed: the pin says it was measured on this exact program, whose sha256 is named above)' if src.startswith('given')
               else f' (replayed by slow_report.py on the registering machine just before registration and equal to {pin_phrase})' if src.startswith('replayed') else '')
        L.append(f"- Self-check of `{spec}` on this build (12 fixed games, t-altaria v t-suicune): `{txt}`{how}. The same pilot code on another build must print the same digest.")
    if stage != 'use':
        L.append('- An `ext:` pilot is an external process asked for every decision (PROTOCOL.md); it may be as slow as it likes. Nothing is a failure for being slow.\n')
    else:
        L.append('')
    L.append('## Design\n')
    L.append(f"- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.")
    L.append(f"- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `{seed_base} + p x {stride} + i`; each deal is played with the deck in seats {seats}. {deals} deals x {len(seats)} seats x 2 arms per pair; {len(pairs)} pairs; **{games} games in all**.")
    L.append(f"- Threads: {manifest['threads']} (they change nothing about the results: every game is seeded). Logging: `{manifest['log_level']}`. Every finished game is appended to `games.jsonl` before the next starts; a stopped run resumes by skipping the games already there.\n")
    L.append('## Decks under test\n')
    L.append('| deck | file | sha256 (first 12) |\n|---|---|---|')
    for d in manifest['decks']:
        L.append(f"| {d['name']} | `{d['path']}` | {d['sha256'][:12]} |")
    L.append('\n## Opponents\n')
    L.append(', '.join(f"{d['name']}" for d in manifest['opponents']) + '\n')
    L.append('## Held-out decks\n')
    if stage == 'use':
        L.append(f"Stage `use`: a report on a deck, not development, so it is allowed on any deck and is **not development evidence**: nothing in it may be used to tune or choose a pilot. "
                 f"Held-out list `{held_names or '(none named yet)'}`, lock `{'on' if held.get('locked', True) else 'off'}`, unchanged by this run. Held-out decks in this run: `{held_in_run or '(none)'}`. "
                 f"The manifest lists no held-out names for the program's own guard (`heldout_decks`), which would refuse them; the names are kept under `heldout_registry` and `heldout_in_run`.\n")
    else:
        L.append(f"Stage `{stage}`; held-out list `{held_names or '(none named yet)'}`, lock `{'on' if held.get('locked', True) else 'off'}`. A development run refuses any held-out deck on either side.\n")
    if cfg.get('slow_report'):
        sr = cfg['slow_report']
        L.append('## Slow report\n')
        L.append(f"**{sr.get('headline', 'slow report')}**. " + (sr.get('summary') or '') + '\n')
        for k in ('deck_file', 'deck_file_sha256', 'deck_file_state', 'deals', 'paired', 'pin', 'program_route', 'pinned_program', 'pinned_program_sha256',
                  'harness_source_sha256', 'harness_source_checkout_sha256', 'engine_ref', 'engine_tree', 'pin_committed', 'pin_committed_detail', 'registered_on',
                  'build_record', 'school_rule', 'school_days'):
            if k in sr:
                v = sr[k]
                if isinstance(v, dict):
                    v = json.dumps(v, sort_keys=True, ensure_ascii=False)
                # a null entry is said in words, not as the text None: for a fact about the checkout it means the checkout had no such file or commit ('not found'); for the pin's
                # detail (nothing to explain when it is committed) and for the build record (the pinned binary has none) it means there is nothing ('none')
                L.append(f"- {k}: `{('none' if k in ('pin_committed_detail', 'build_record') else 'not found') if v is None else v}`")
        L.append('')
    L.append('## Analysis plan (fixed now)\n')
    if stage == 'use':
        L.append('- Score of a game for the deck: win 1, tie 0.5, loss 0. The page (`SLOW_REPORT.md`) reports the deck\'s score over the pilot\'s games, overall and against each opponent list, each with a **Wilson 95% range** (valid at 0% and 100% and for few games), and by who went first.')
        if (cfg.get('slow_report') or {}).get('paired', True):
            L.append('- The baseline comparison is **on** (the default): the **paired difference** `d = score(arm X) - score(arm ref)` on each (deck, opponent, deal, seat), reported as its mean with a **Student t 95% interval** over the paired games (a deal and seat played by both pilots), and what that range does and does not include.')
        else:
            L.append('- The baseline comparison is **off** (`--no-paired`): the reference still plays the deck on the same deals (about a second a game, it is part of the registered games) but the page leaves the paired difference out.')
        L.append('- The page states its question before its size, says which games each range refers to, and says what a wide range can and cannot answer; it has no pass or fail line. `REPORT.md` is the engineering view of the same games (it uses mean ± 1.96·sd/√n for its paired tables) and is a detail, not the headline.')
    else:
        L.append('- Score of a game for the deck: win 1, tie 0.5, loss 0. **Paired difference** `d = score(arm X) - score(arm ref)` on each (deck, opponent, deal, seat).')
        L.append('- Reported per (deck, opponent) pair, per deck pooled over its opponents, and pooled over everything: the mean of `d` with the interval **mean ± 1.96·sd/√n** (sample sd, n = paired games). A second pooled figure weights every deck equally.')
        L.append('- Also reported: the same split by who went first (the first player is identical in both arms), win rates per arm, wall time and decisions per game for each pilot, cost per game when an external pilot reports it, and how many more deals would narrow the pooled interval to ±3 and ±5 points at the sd reached.')
    L.append(f"- Intended-line rates from `{lines_path}`" + (f" (sha256 `{lines_sha[:12]}`)" if lines_sha else ' (file not found when registered)') + ': per game and per use, per arm, with the paired difference where it is per game.')
    L.append('- No pass/fail threshold is set by this document. A slow pilot is reported with its time and cost, not rejected.\n')
    L.append('## Run\n')
    srb = cfg.get('slow_report') or {}
    if srb.get('resume_command'):
        days = srb.get('school_days')
        rule = ('applies the school-morning rule as registered' + (f' ({days})' if days else ' (no school days)' if days == '' else '') if srb.get('school_rule', 'on') == 'on'
                else 'does NOT apply the school-morning rule (chosen at registration: it never pauses for school mornings)')
        prog_txt = ('the program it was registered with, a rebuild of the pinned source by its build record (accepted after both self-checks were replayed on the registering machine; a resume needs the same sha256, or a rebuild whose build record has the same engine tree and harness hash and whose two self-checks are replayed again)'
                    if srb.get('program_route') == 'rebuilt' else 'the pinned program')
        L.append(f'A slow report is run and resumed through its wrapper, which removes the variables that would tune the pilot or change the rules from the program\'s environment, {rule}, '
                 f'and checks the registration, the deck files and {prog_txt} before every sitting:\n')
        L.append('```\n' + srb['resume_command'] + '\n```')
    else:
        L.append('```\nstrength run --manifest manifest.json --out .   # add --max-games N or --stop-after-min M to stop early; run it again to resume\npython3 strength_report.py --dir .\n```')
    with open(os.path.join(a.out, 'PREREGISTRATION.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    with open(os.path.join(a.out, 'manifest.sha256'), 'w') as f:  # last: its presence says the registration is complete
        f.write(msha + '  manifest.json\n')
    print(f"pre-registered {games} games ({len(pairs)} pair{'' if len(pairs) == 1 else 's'}, {deals} deal{'' if deals == 1 else 's'} x {len(seats)} seat{'' if len(seats) == 1 else 's'} x 2 arms) in {a.out}")
    print('manifest sha256', msha)


if __name__ == '__main__':
    main()
