#!/usr/bin/env python3
"""Engine candidate self-checks: replay one recorded rules-switch-2 reference with another program set and compare.
(replay2.py: replay.py of Oct 20 plus side f, the final candidate; a legality_scan, CLI or run_screen replay on side f is
also compared with the Oct 20 build's own output of the same run, games/new/NAME.*, where it exists: "v new".)

  replay.py SIDE NAME      SIDE = old | new | u | f ; NAME = a reference base name in rl/results/engine_switch_rules2_2026-10/
                           (e.g. 08a9b3a_table_k3), or floor:<page_id> (a floor_7c page)
The reference's own .run record gives the program, the working folder and the arguments. Paths are mapped:
  /home/dacz8976/engine-rules2-08a9b3a/engine  ->  <side's archive>/engine   (the archive of the side's commit: engine + decks)
  /mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim  ->  /home/dacz8976/pincand  (main's decks and pairs files, unchanged)
Output: $W/games/<side>/<NAME>.{jsonl,txt,cmd,cmp}; one line appended to $W/games/summary.tsv:
  side  name  games  seconds  verdict(SAME|DIFFERS|ERROR)  detail
For DIFFERS, <NAME>.diff.tsv lists every differing deal (pairing, i, the fields that differ, both decks, both winners).
legality_scan runs with RAYON_NUM_THREADS (default 8; games are matched by (pairing, i), so the thread count changes no game);
the CLI, run_screen and floor.py run as recorded, without RAYON_NUM_THREADS. Everything runs at nice 19 / ionice -c3."""
import hashlib, json, os, shlex, subprocess, sys, time
from pathlib import Path

W = Path('/home/dacz8976/pincand_work')
R = Path('/home/dacz8976/pincand')
SW2 = R / 'rl/results/engine_switch_rules2_2026-10'
OLD_CWD = '/home/dacz8976/engine-rules2-08a9b3a/engine'
WIN = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
SIDES = {'old': (W / 'O', W / 'programs/O'), 'new': (W / 'N', W / 'programs/N'), 'u': (W / 'U', W / 'programs/U'),
         'f': (W / 'F', W / 'programs/F')}
THREADS = os.environ.get('SCAN_THREADS', '8')
GENTLE = ['nice', '-n', '19', 'ionice', '-c3']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_run(name):
    lines = (SW2 / f'{name}.run').read_text().splitlines()
    prog, _, psha = lines[0].split(' ', 2)
    psha = psha.replace('sha256 ', '').strip()
    cwd = next(l[4:] for l in lines if l.startswith('cwd '))
    args = shlex.split(next(l[5:] for l in lines if l.startswith('args ')))
    return prog, psha, cwd, args


def mapped(s, archive):
    return s.replace(OLD_CWD, str(archive / 'engine')).replace(WIN, str(R))


def summary(side, name, games, secs, verdict, detail):
    with open(W / 'games/summary.tsv', 'a') as f:
        f.write(f'{side}\t{name}\t{games}\t{secs}\t{verdict}\t{detail}\n')
    print(f'{side} {name}: {verdict} ({games} games, {secs} s) {detail}', flush=True)


def diff_jsonl(new, ref, out_tsv):
    def load(p):
        d = {}
        for l in open(p):
            g = json.loads(l)
            d[(g['pairing'], g['i'])] = g
        return d
    a, b = load(new), load(ref)
    rows = []
    for k in sorted(set(a) | set(b)):
        x, y = a.get(k), b.get(k)
        if x is None or y is None:
            rows.append((k, 'MISSING_IN_' + ('NEW' if x is None else 'REF'), '', '', '', ''))
            continue
        fields = sorted(f for f in set(x) | set(y) if x.get(f, '<absent>') != y.get(f, '<absent>'))
        if fields:
            rows.append((k, ','.join(fields), x.get('a', ''), x.get('b', ''), x.get('winner_seat'), y.get('winner_seat')))
    with open(out_tsv, 'w') as f:
        f.write('pairing\ti\tfields\ta\tb\twinner_new\twinner_ref\n')
        for (p, i), fl, da, db, wn, wr in rows:
            f.write(f'{p}\t{i}\t{fl}\t{da}\t{db}\t{wn}\t{wr}\n')
    return len(rows), len(a), len(b)


def main():
    side, name = sys.argv[1], sys.argv[2]
    archive, progs = SIDES[side]
    out = W / 'games' / side
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    for k in list(env):
        if k.startswith('DECKGYM_'):
            sys.exit(f'refusing: {k} is set')
    env.pop('RAYON_NUM_THREADS', None)
    env.pop('PDL_DB', None)
    t0 = time.time()

    if name.startswith('floor:'):
        pid = name.split(':', 1)[1]
        rows = [l.split('\t') for l in (SW2 / 'floor_7c.tsv').read_text().splitlines() if l and not l.startswith(('#', 'page_id'))]
        row = next(r for r in rows if r[0] == pid)
        nm, deck, mode = row[1], row[4], row[8].strip()
        gym = progs / 'deckgym'
        d = out / f'floor_{pid}'
        if d.exists():
            subprocess.run(['rm', '-rf', str(d)])
        d.mkdir(parents=True)
        cmd = GENTLE + ['python3', str(SW2 / 'floor_with.py'), str(gym), sha(gym), str(R / 'decks/screen/floor.py'), deck, '--out', str(d)]
        (out / f'floor_{pid}.cmd').write_text(' '.join(shlex.quote(c) for c in cmd) + '\n')
        with open(out / f'floor_{pid}.txt', 'w') as log:
            rc = subprocess.run(cmd, cwd=R, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
        secs = int(time.time() - t0)
        if rc != 0:
            return summary(side, name, 0, secs, 'ERROR', f'floor.py exit {rc}')
        opts = ['--allow-coverage-program']
        for tok in mode.split(','):
            if tok.startswith('report-opponent:'):
                opts += ['--report-opponent', tok.split(':', 1)[1]]
            elif tok.startswith('caveat:'):
                opts += ['--allow-caveat', tok.split(':', 1)[1]]
        chk = subprocess.run(['python3', str(SW2 / 'sitting1_check.py'), 'floor', str(d), str(SW2 / 'floor_7c' / pid), nm, '--label', f'{side} floor {pid}'] + opts,
                             cwd=R, capture_output=True, text=True)
        (out / f'floor_{pid}.cmp').write_text(chk.stdout + chk.stderr)
        games = sum(1 for _ in open(d / f'{nm}_games.jsonl'))
        verdict = 'SAME' if chk.returncode == 0 else ('DIFFERS' if chk.returncode == 1 else 'ERROR')
        return summary(side, name, games, secs, verdict, (chk.stdout.strip().splitlines() or [''])[-1][:300])

    prog, psha, cwd, args = read_run(name)
    exe = progs / prog
    cwd = mapped(cwd, archive)
    args = [mapped(a, archive) for a in args]
    if prog == 'legality_scan':
        env['RAYON_NUM_THREADS'] = THREADS
        part = out / f'{name}.jsonl'
        cmd = GENTLE + [str(exe)] + args + ['--games-out', str(part)]
    elif prog == 'deckgym' and args and args[0] == 'simulate':
        cmd = GENTLE + [str(exe)] + args
    elif prog == 'goldfish':
        cov = out / f'{name}_coverage.json'
        args = [str(cov) if a.endswith('_coverage.json') else a for a in args]
        cmd = GENTLE + [str(exe)] + args
    elif prog == 'deckgym' and args and args[0].startswith('run_screen.py='):
        rest = args[2:]
        cmd = GENTLE + ['python3', str(R / 'rl/results/engine_switch_2026-09-30/screen_with.py'), str(exe), sha(exe), str(R / 'decks/screen/run_screen.py')] + rest
    else:
        sys.exit(f'unknown run kind: {prog} {args[:2]}')
    (out / f'{name}.cmd').write_text(f'cwd {cwd}\n' + ' '.join(shlex.quote(c) for c in cmd) + f'\nprogram sha256 {sha(exe)}\n')
    with open(out / f'{name}.txt', 'w') as log:
        rc = subprocess.run(cmd, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
    secs = int(time.time() - t0)
    if rc != 0:
        return summary(side, name, 0, secs, 'ERROR', f'exit {rc}; see {name}.txt')

    ck = SW2 / 'switch_check.py'
    if prog == 'legality_scan':
        ref = SW2 / f'{name}.jsonl'
        nref = sum(1 for _ in open(ref))
        chk = subprocess.run(['python3', str(ck), 'same', str(part), '--ref', str(ref), '--expect', str(nref), '--label', f'{side} {name}'],
                             capture_output=True, text=True)
        (out / f'{name}.cmp').write_text(chk.stdout + chk.stderr)
        rules = subprocess.run(['python3', str(ck), 'rules', str(out / f'{name}.txt')], capture_output=True, text=True)
        ndiff, na, nb = diff_jsonl(part, ref, out / f'{name}.diff.tsv')
        verdict = 'SAME' if chk.returncode == 0 else ('DIFFERS' if chk.returncode == 1 else 'ERROR')
        vnew = ''
        cnew = W / 'games/new' / f'{name}.jsonl'
        if side == 'f' and cnew.exists():
            chk2 = subprocess.run(['python3', str(ck), 'same', str(part), '--ref', str(cnew), '--expect', str(nref), '--label', f'f v new {name}'],
                                  capture_output=True, text=True)
            (out / f'{name}.v_new.cmp').write_text(chk2.stdout + chk2.stderr)
            nd2, _, _ = diff_jsonl(part, cnew, out / f'{name}.v_new.diff.tsv')
            vnew = f' | v new: {"SAME" if chk2.returncode == 0 else ("DIFFERS" if chk2.returncode == 1 else "ERROR")} ({nd2} deals)'
        return summary(side, name, na, secs, verdict, f'{ndiff} differing deals of {nb}{vnew}; rules page: {rules.stdout.strip()[:120]}')
    if prog == 'deckgym' and args[0] == 'simulate':
        strip = lambda t: [l for l in t.splitlines() if not l.startswith('Ran ')]
        new_t, ref_t = (out / f'{name}.txt').read_text(), (SW2 / f'{name}.txt').read_text()
        same = strip(new_t) == strip(ref_t)
        wins = ' | '.join(l for l in new_t.splitlines() if 'won' in l or 'Draws' in l)
        cnew = W / 'games/new' / f'{name}.txt'
        if side == 'f' and cnew.exists():
            wins += ' | v new: ' + ('SAME' if strip(new_t) == strip(cnew.read_text()) else 'DIFFERS')
        return summary(side, name, 240, secs, 'SAME' if same else 'DIFFERS', wins)
    if prog == 'goldfish':
        norm = lambda t: t.replace(str(R), WIN)
        same_t = norm((out / f'{name}.txt').read_text()) == (SW2 / f'{name}.txt').read_text()
        same_c = norm(cov.read_text()) == (SW2 / f'{name}_coverage.json').read_text()
        return summary(side, name, 0, secs, 'SAME' if (same_t and same_c) else 'DIFFERS', f'page {"=" if same_t else "!="}, coverage {"=" if same_c else "!="}')
    chk = subprocess.run(['python3', str(ck), 'screen', str(out / f'{name}.txt'), str(SW2 / f'{name}.txt')], capture_output=True, text=True)
    (out / f'{name}.cmp').write_text(chk.stdout + chk.stderr)
    detail = chk.stdout.strip()[:300]
    cnew = W / 'games/new' / f'{name}.txt'
    if side == 'f' and cnew.exists():
        chk2 = subprocess.run(['python3', str(ck), 'screen', str(out / f'{name}.txt'), str(cnew)], capture_output=True, text=True)
        detail += ' | v new: ' + ('SAME' if chk2.returncode == 0 else ('DIFFERS' if chk2.returncode == 1 else 'ERROR'))
    return summary(side, name, 3840, secs, 'SAME' if chk.returncode == 0 else ('DIFFERS' if chk.returncode == 1 else 'ERROR'), detail)


if __name__ == '__main__':
    main()
