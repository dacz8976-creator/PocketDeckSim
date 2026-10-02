#!/usr/bin/env python3
"""Pre-registration for a strength run: writes the manifest the program executes and PREREGISTRATION.md, before any game is played.

  strength_prereg.py --config CONFIG.json --out RUNDIR [--repo ROOT]

CONFIG.json (all keys but the first four optional):
  name, question          what this run is for, in a sentence
  pilot, reference        pilot specs: an engine pilot code (km3, kog3, ...) or `ext:<command>` for an external process
  deck_groups, decks      decks under test: group names from groups.json, and/or single deck names from decks.json
  opponent_groups, opponents   the opponent pool, the same way (default: the same as the decks under test)
  deals (default 200), seats ([0, 1]), seed_base, pair_stride (10000), threads (2), log_level (deck | full | none), ext_timeout_s
  stage                   dev (default) or heldout. A held-out deck is refused unless stage is heldout AND heldout.json says locked: false
  intended_lines          path of the intended-lines file (default rl/strength/intended_lines.json)
  program, program_sha256, engine, pilot_provenance, reference_provenance   free text recorded as given (build.sh prints them)

Refuses to write into a run directory that already holds games. The manifest's sha256 is written beside it and into the README; the report
checks that the manifest still matches.
"""
import argparse, hashlib, json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--repo', default=os.path.abspath(os.path.join(HERE, '..', '..')))
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding='utf-8'))
    root = a.repo
    reg = json.load(open(os.path.join(HERE, 'decks.json'), encoding='utf-8'))['decks']
    groups = json.load(open(os.path.join(HERE, 'groups.json'), encoding='utf-8'))
    held = json.load(open(os.path.join(HERE, 'heldout.json'), encoding='utf-8'))
    held_names = list(held.get('decks', []))
    stage = cfg.get('stage', 'dev')

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

    decks = expand(cfg.get('deck_groups'), cfg.get('decks'))
    if not decks:
        sys.exit('no decks under test (deck_groups / decks)')
    opps = expand(cfg.get('opponent_groups'), cfg.get('opponents')) if (cfg.get('opponent_groups') or cfg.get('opponents')) else list(decks)
    # the held-out guard (by name and by file content, so a renamed copy does not slip through)
    held_hashes = {sha(os.path.join(root, reg[n])): n for n in held_names if n in reg}
    for n in decks + opps:
        if n in held_names or sha(os.path.join(root, reg[n])) in held_hashes:
            if stage != 'heldout' or held.get('locked', True):
                sys.exit(f'REFUSED: {n} is a held-out deck. A development run never uses it; it is unlocked only when heldout.json says locked: false and the run says stage: heldout.')
    if stage == 'heldout' and held.get('locked', True):
        sys.exit('REFUSED: stage heldout, but heldout.json is still locked.')

    os.makedirs(a.out, exist_ok=True)
    if os.path.exists(os.path.join(a.out, 'games.jsonl')):
        sys.exit('this run directory already holds games; pre-registration comes first')
    deals = int(cfg.get('deals', 200))
    seats = cfg.get('seats', [0, 1])
    stride = int(cfg.get('pair_stride', 10000))
    seed_base = int(cfg.get('seed_base', 24_300_000_000))
    pairs = [(d, o) for d in decks for o in opps if d != o]
    games = len(pairs) * deals * len(seats) * 2
    lines_path = cfg.get('intended_lines', 'rl/strength/intended_lines.json')
    lines_abs = os.path.join(root, lines_path) if not os.path.isabs(lines_path) else lines_path
    lines_sha = sha(lines_abs) if os.path.exists(lines_abs) else None
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # provenance: the program's own hash, the repository commit, and a digest of 12 fixed games for each engine pilot (two builds that play
    # the same reference pilot must print the same digest)
    import subprocess
    prog = cfg.get('program')
    prog_sha = cfg.get('program_sha256')
    if prog and os.path.isfile(prog):
        actual = sha(prog)
        if prog_sha and prog_sha != actual:
            sys.exit(f'program_sha256 in the config ({prog_sha[:12]}) is not the program at {prog} ({actual[:12]})')
        prog_sha = actual
    try:
        repo_commit = subprocess.run(['git', '-C', root, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip() or None
    except Exception:
        repo_commit = None
    selfcheck = {}
    if prog and os.path.isfile(prog):
        da, db = reg.get('t-altaria'), reg.get('t-suicune')
        for spec in sorted({cfg['pilot'], cfg['reference']}):
            if spec.startswith('ext:') or not da or not db:
                continue
            r = subprocess.run([prog, 'selfcheck', '--root', root, '--pilot', spec, '--deck-a', da, '--deck-b', db, '--games', '12'], capture_output=True, text=True)
            selfcheck[spec] = r.stdout.strip() or ('failed: ' + r.stderr.strip()[-200:])

    manifest = {
        'name': cfg.get('name', os.path.basename(os.path.normpath(a.out))), 'question': cfg.get('question', ''),
        'repo_commit': repo_commit, 'selfcheck': selfcheck,
        'created_at': now, 'stage': stage, 'repo_root': root,
        'pilot': cfg['pilot'], 'reference': cfg['reference'],
        'decks': [{'name': n, 'path': reg[n], 'sha256': sha(os.path.join(root, reg[n]))} for n in decks],
        'opponents': [{'name': n, 'path': reg[n], 'sha256': sha(os.path.join(root, reg[n]))} for n in opps],
        'deals': deals, 'seats': seats, 'seed_base': seed_base, 'pair_stride': stride, 'threads': int(cfg.get('threads', 2)),
        'log_level': cfg.get('log_level', 'deck'), 'ext_timeout_s': cfg.get('ext_timeout_s'),
        'heldout_decks': held_names, 'heldout_locked': held.get('locked', True),
        'intended_lines': lines_path, 'intended_lines_sha256': lines_sha,
        'program': cfg.get('program'), 'program_sha256': prog_sha, 'engine': cfg.get('engine'),
        'pilot_provenance': cfg.get('pilot_provenance'), 'reference_provenance': cfg.get('reference_provenance'),
        'planned_pairs': len(pairs), 'planned_games': games,
    }
    mpath = os.path.join(a.out, 'manifest.json')
    if os.path.exists(mpath):
        sys.exit('manifest.json already exists in this run directory; pre-registration is written once (use a new directory)')
    open(mpath, 'w', encoding='utf-8').write(json.dumps(manifest, indent=1, ensure_ascii=False))
    msha = sha(mpath)
    open(os.path.join(a.out, 'manifest.sha256'), 'w').write(msha + '  manifest.json\n')

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
        L.append(f"- Self-check of `{spec}` on this build (12 fixed games, t-altaria v t-suicune): `{txt}`. The same pilot code on another build must print the same digest.")
    L.append('- An `ext:` pilot is an external process asked for every decision (PROTOCOL.md); it may be as slow as it likes. Nothing is a failure for being slow.\n')
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
    L.append(f"Stage `{stage}`; held-out list `{held_names or '(none named yet)'}`, lock `{'on' if held.get('locked', True) else 'off'}`. A development run refuses any held-out deck on either side.\n")
    L.append('## Analysis plan (fixed now)\n')
    L.append('- Score of a game for the deck: win 1, tie 0.5, loss 0. **Paired difference** `d = score(arm X) - score(arm ref)` on each (deck, opponent, deal, seat).')
    L.append('- Reported per (deck, opponent) pair, per deck pooled over its opponents, and pooled over everything: the mean of `d` with the interval **mean ± 1.96·sd/√n** (sample sd, n = paired games). A second pooled figure weights every deck equally.')
    L.append('- Also reported: the same split by who went first (the first player is identical in both arms), win rates per arm, wall time and decisions per game for each pilot, cost per game when an external pilot reports it, and how many more deals would narrow the pooled interval to ±3 and ±5 points at the sd reached.')
    L.append(f"- Intended-line rates from `{lines_path}`" + (f" (sha256 `{lines_sha[:12]}`)" if lines_sha else ' (file not found when registered)') + ': per game and per use, per arm, with the paired difference where it is per game.')
    L.append('- No pass/fail threshold is set by this document. A slow pilot is reported with its time and cost, not rejected.\n')
    L.append('## Run\n')
    L.append('```\nstrength run --manifest manifest.json --out .   # add --max-games N or --stop-after-min M to stop early; run it again to resume\npython3 strength_report.py --dir .\n```')
    open(os.path.join(a.out, 'PREREGISTRATION.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(f'pre-registered {games} games ({len(pairs)} pairs, {deals} deals x {len(seats)} seats x 2 arms) in {a.out}')
    print('manifest sha256', msha)


if __name__ == '__main__':
    main()
