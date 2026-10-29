#!/usr/bin/env python3
"""Engine candidate, release follow-through: re-run every floor re-check page of rl/results/floor_recheck_rules2_2026-10/ on the
candidate deckgym (floor_with.py / screen_with.py stand-ins; the manifest's goldfish d8cfb779 for coverage, as every reference
used) and compare with the recorded page (sitting1_check.py floor, no modes; switch_check.py screen for run_screen).
  floor2.py [PIECE ...]       (default: all 12, in order; a piece already in summary.tsv is skipped)
Guards: the candidate deckgym's sha256; the working tree's project_manifest.json is HEAD's (no draft engine); an empty output
folder; after the run, the page's Engine line names the candidate program exactly once (run_screen: twice); 1,920 games per page.
Output /home/dacz8976/pincand_work/floor2/<piece>/ and floor2/summary.tsv: piece, games, seconds, SAME|DIFFERS|ERROR, detail.
Another program set (the final candidate): FLOOR2_GYM, FLOOR2_SHA, FLOOR2_REL (the path the page's Engine line will name),
FLOOR2_OUT; with FLOOR2_ALSO_VS=<an earlier floor2 output folder>, a page that differs from the recorded one is also compared
with that run's page of the same piece (attribution: the final candidate v the candidate without the new items)."""
import hashlib, os, shlex, shutil, subprocess, sys, time
from pathlib import Path

R = Path('/home/dacz8976/pincand')
W = Path('/home/dacz8976/pincand_work')
OUT = Path(os.environ.get('FLOOR2_OUT', str(W / 'floor2')))
ALSO_VS = os.environ.get('FLOOR2_ALSO_VS')
REF = R / 'rl/results/floor_recheck_rules2_2026-10'
SW = R / 'rl/results/engine_switch_rules2_2026-10'
FW = SW / 'floor_with.py'
SCW = R / 'rl/results/engine_switch_2026-09-30/screen_with.py'
CK = SW / 'sitting1_check.py'
SC = SW / 'switch_check.py'
FLOOR = R / 'decks/screen/floor.py'
GYM = Path(os.environ.get('FLOOR2_GYM', str(R / 'rl/results/engine_candidate_2026-10-20/programs/deckgym')))
GSHA = os.environ.get('FLOOR2_SHA', '245e11e8cf939da7ba12a50fbb18630c67b1fb2231a692dd0c259c4a01556745')
REL = os.environ.get('FLOOR2_REL', os.path.relpath(GYM, R))  # what floor.py prints: the program relative to the repo
DFIRST = 'rl/results/engine_switch_rules2_2026-10/floor_7c/d_first/draft-D-entei-grimhound.txt'
DNAME = 'draft-D-entei-grimhound'
GENTLE = ['nice', '-n', '19', 'ionice', '-c3']

# piece: (kind, deck or None, extra floor.py args, ref dir, page name)
PIECES = {
    'B_D_victini-passive': ('victini', DFIRST, [], 'STRIP:D_victini-passive', DNAME),
    'A_brew-06': ('floor', 'decks/brews/brew-06-pyukumuku-silvally-payback.txt', [], REF, 'brew-06-pyukumuku-silvally-payback'),
    'A_brew-06b': ('floor', 'decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt', [], REF, 'brew-06b-pyukumuku-silvally-scyther-grass'),
    'A_control14_k3': ('floor', 'decks/dustin/14-comfey-raticate-hypno.txt', ['--pilot', 'k3', '--meta-pilot', 'k3'], REF / 'control_k3', '14-comfey-raticate-hypno'),
    'A_brew-05b': ('floor', 'decks/brews/brew-05b-meowstic-hatterene-comfey.txt', [], REF, 'brew-05b-meowstic-hatterene-comfey'),
    'A_07': ('floor', 'decks/dustin/07-skarmory-stall.txt', [], REF, '07-skarmory-stall'),
    'A_run_screen': ('screen', None, [], REF / 'run_screen.txt', 'run_screen'),
    'B_12': ('floor', 'decks/dustin/12-ariados-whimsicott-ogerpon.txt', [], REF / 'pages/12', '12-ariados-whimsicott-ogerpon'),
    'B_brew-07': ('floor', 'decks/brews/brew-07-hoopa-darkrai-sableye.txt', [], REF / 'pages/brew-07', 'brew-07-hoopa-darkrai-sableye'),
    'B_brew-09': ('floor', 'decks/brews/brew-09-sableye-obstagoon.txt', [], REF / 'pages/brew-09', 'brew-09-sableye-obstagoon'),
    'B_D_root': ('floor', DFIRST, [], 'STRIP:D_root', DNAME),
    'B_D_amended': ('floor', 'decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt', [], 'STRIP:D_amended', DNAME),
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def summary(piece, games, secs, verdict, detail):
    with open(OUT / 'summary.tsv', 'a') as f:
        f.write(f'{piece}\t{games}\t{secs}\t{verdict}\t{detail}\n')
    print(f'{piece}: {verdict} ({games} games, {secs} s) {detail}', flush=True)


def stripped_ref(d):
    """The D pages carry a leading '> ...' note and a blank line: compare against a copy without them (games and coverage as is)."""
    dst = OUT / '_ref_stripped' / d
    dst.mkdir(parents=True, exist_ok=True)
    src = REF / 'pages' / d
    for s in ('_games.jsonl', '_coverage.json'):
        shutil.copyfile(src / f'{DNAME}{s}', dst / f'{DNAME}{s}')
    lines = (src / f'{DNAME}.md').read_text(encoding='utf-8').split('\n')
    i = 0
    while i < len(lines) and lines[i].startswith('>'):
        i += 1
    assert i >= 1 and lines[i] == '', (d, i)
    (dst / f'{DNAME}.md').write_text('\n'.join(lines[i + 1:]), encoding='utf-8', newline='\n')
    return dst


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k not in ('RAYON_NUM_THREADS', 'PDL_DB')}
    if any(k.startswith('DECKGYM_') for k in env):
        sys.exit('DECKGYM_* set: refusing')
    if sha(GYM) != GSHA or not os.access(GYM, os.X_OK):
        sys.exit(f'{GYM} is not the tested candidate deckgym {GSHA[:16]} (or not executable)')
    if subprocess.run(['git', '-C', str(R), 'diff', '--quiet', 'HEAD', '--', 'project_manifest.json']).returncode != 0:
        sys.exit('the working tree manifest differs from HEAD: refusing (floor.py would resolve another engine)')
    done = set()
    if (OUT / 'summary.tsv').exists():
        done = {l.split('\t')[0] for l in (OUT / 'summary.tsv').read_text().splitlines() if l}
    for piece in (sys.argv[1:] or list(PIECES)):
        if piece in done:
            continue
        kind, deck, extra, ref, name = PIECES[piece]
        d = OUT / piece
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        t0 = time.time()
        if kind == 'screen':
            cmd = GENTLE + ['python3', str(SCW), str(GYM), GSHA, str(R / 'decks/screen/run_screen.py'),
                            'decks/brews/brew-06-pyukumuku-silvally-payback.txt', 'decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt', '--games', '240']
        elif kind == 'victini':
            vp = REF / 'pages/D_victini-passive'
            cmd = GENTLE + ['python3', str(FW), str(GYM), GSHA, str(vp / 'run_copy.py'), str(vp / 'floor_victini_passive.py'), str(FLOOR), deck, '--out', str(d)]
        else:
            cmd = GENTLE + ['python3', str(FW), str(GYM), GSHA, str(FLOOR), deck] + extra + ['--out', str(d)]
        (d / 'cmd.txt').write_text('cwd ' + str(R) + '\n' + ' '.join(shlex.quote(c) for c in cmd) + '\n')
        log = d / ('run_screen.txt' if kind == 'screen' else 'run.log')
        with open(log, 'w') as f:
            rc = subprocess.run(cmd, cwd=R, env=env, stdout=f, stderr=subprocess.STDOUT).returncode
        secs = int(time.time() - t0)
        if rc != 0:
            summary(piece, 0, secs, 'ERROR', f'exit {rc}; see {log}')
            continue
        if kind == 'screen':
            n = log.read_text().count(f'; engine {REL})')
            if n != 2:
                summary(piece, 0, secs, 'ERROR', f'engine guard: "{REL}" appears {n} times, not 2')
                continue
            chk = subprocess.run(['python3', str(SC), 'screen', str(log), str(ref)], capture_output=True, text=True)
            (d / 'cmp.txt').write_text(chk.stdout + chk.stderr)
            v = 'SAME' if chk.returncode == 0 else ('DIFFERS' if chk.returncode == 1 else 'ERROR')
            detail = chk.stdout.strip()[:250]
            if v == 'DIFFERS' and ALSO_VS and (Path(ALSO_VS) / piece / 'run_screen.txt').exists():
                chk3 = subprocess.run(['python3', str(SC), 'screen', str(log), str(Path(ALSO_VS) / piece / 'run_screen.txt')], capture_output=True, text=True)
                (d / 'cmp_also_vs.txt').write_text(chk3.stdout + chk3.stderr)
                detail += f' | v {Path(ALSO_VS).name}: exit {chk3.returncode}'
            summary(piece, 3840, secs, v, detail)
            continue
        md = d / f'{name}.md'
        games = d / f'{name}_games.jsonl'
        if not md.exists() or not games.exists():
            summary(piece, 0, secs, 'ERROR', f'no {md.name} or {games.name}')
            continue
        guard = sum(1 for l in md.read_text(encoding='utf-8').splitlines() if l.startswith(f'- Engine: {REL} '))
        ng = sum(1 for _ in open(games))
        if guard != 1 or ng != 1920:
            summary(piece, ng, secs, 'ERROR', f'engine guard {guard} (want 1), games {ng} (want 1920)')
            continue
        refdir = stripped_ref(ref.split(':', 1)[1]) if isinstance(ref, str) and ref.startswith('STRIP:') else ref
        # the victini copy's page starts with the copy note too: compare without it, like the reference
        if kind == 'victini':
            lines = md.read_text(encoding='utf-8').split('\n')
            i = 0
            while i < len(lines) and lines[i].startswith('>'):
                i += 1
            if i:
                assert lines[i] == ''
                shutil.copyfile(md, d / f'{name}.with_note.md')
                md.write_text('\n'.join(lines[i + 1:]), encoding='utf-8', newline='\n')
        chk = subprocess.run(['python3', str(CK), 'floor', str(d), str(refdir), name, '--label', f'cand {piece}'], capture_output=True, text=True)
        (d / 'cmp.txt').write_text(chk.stdout + chk.stderr)
        v = 'SAME' if chk.returncode == 0 else ('DIFFERS' if chk.returncode == 1 else 'ERROR')
        detail = (chk.stdout.strip().splitlines() or [''])[-1][:250]
        if v == 'DIFFERS':
            chk2 = subprocess.run(['python3', str(CK), 'floor', str(d), str(refdir), name, '--label', f'cand {piece} (t-lucario set aside)',
                                   '--report-opponent', 't-lucario'], capture_output=True, text=True)
            (d / 'cmp_report_t-lucario.txt').write_text(chk2.stdout + chk2.stderr)
            detail += f' | with t-lucario reported apart: exit {chk2.returncode}'
            if ALSO_VS and (Path(ALSO_VS) / piece / f'{name}.md').exists():
                chk3 = subprocess.run(['python3', str(CK), 'floor', str(d), str(Path(ALSO_VS) / piece), name, '--label', f'{piece} v {ALSO_VS}'],
                                      capture_output=True, text=True)
                (d / 'cmp_also_vs.txt').write_text(chk3.stdout + chk3.stderr)
                detail += f' | v {Path(ALSO_VS).name}: exit {chk3.returncode}'
        summary(piece, ng, secs, v, detail)


if __name__ == '__main__':
    main()
