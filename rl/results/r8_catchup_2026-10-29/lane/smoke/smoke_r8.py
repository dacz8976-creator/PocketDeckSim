#!/usr/bin/env python3
"""smoke_r8.py PLAN PROGRAM ROOT OUTDIR: the Lane N smoke (coordinator-147 §4, coordinator-148 §2.3 and §2.6), one game at a time.

PLAN   b_km3: the rule-row / item 11 decks, km3 v km3 only (148 §2.6): b01-b04 v t-altaria, and b05 (Urshifu) v b06 (Snover, Sealeo)
       a_km3: the 9 decks a01-a09 that hold the 55 newly supported printings, km3 v km3, v t-altaria
       a_kx3: the same 9 decks and deals, kx3 on the deck v km3 on t-altaria (the ref arm is km3 v km3 again)
PROGRAM a `strength` build (rl/strength/build.sh): the lane's own build for km3, K8's for kx3.
ROOT   the lane worktree (deck paths in the manifests are relative to it; `strength run` hashes nothing, it reads them).
Each deck plays 2 deals x 2 seats = 4 games per arm; `strength run` always plays both arms (X = PLAN's pilot on the deck,
ref = km3 on the deck), so a km3 plan plays every game twice and the two must be identical (km3 is deterministic: README).
Seeds: an unregistered smoke block, a: 25,100,000,000, b01-b04: 25,200,000,000, b05: 25,300,000,000 (+ deck x 10,000,000 + deal).
Every game is its own `strength run --threads 1 --max-games 1` (resumable: games.jsonl), with log_level full (every asked
decision of both seats, with its milliseconds, turn, action, legal-action count, points, Active and Bench size).
Between games: wait while /home/dacz8976/credit_work/PAUSE exists.
Rules (148): a refusal (exit 2) or a panic (errors.jsonl) is a STOP. A km3 decision over 3 s: that game is played again once
(same seed, seat and pilots); over 3 s again: STOP. kx3 is report-only: mean / median / p95 / max ms per decision, every kx3
decision over 30 s named with its board; one kx3 decision over 120 s stops the kx3 smoke (exit 3; the rest of Lane N goes on).
Also a STOP: a km3 plan's two arms differ on a deal; a_kx3's ref arm differs from a_km3's game of the same key.
Exit 0 = as predicted, 1 = STOP, 3 = the kx3 smoke stopped (120 s). Writes OUTDIR/<PLAN>/{SUMMARY.txt,PER_GAME.tsv,SLOW.tsv}."""
import json, math, os, statistics, subprocess, sys, time
from pathlib import Path

PLAN, PROGRAM, ROOT, OUTDIR = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
PAUSE = Path('/home/dacz8976/credit_work/PAUSE')
D = 'rl/results/r8_catchup_2026-10-29/lane/smoke/decks/'
OPP = ('t-altaria', 'decks/screen/opponents/t-altaria.txt')
A = ['a01-grass-honey', 'a02-grass-items', 'a03-fire', 'a04-water', 'a05-lightning', 'a06-psychic-lunala', 'a07-psychic-promo-c',
     'a08-eevee-colorless', 'a09-fighting-metal']
RUNS = {'b_km3': [('b14', 'km3', ['b01-darkrai-sableye', 'b02-iris-haxorus', 'b03-mega-blastoise', 'b04-starting-plains'], [OPP], 25_200_000_000),
                  ('b56', 'km3', ['b05-urshifu'], [('b06-snover-sealeo', D + 'b06-snover-sealeo.txt')], 25_300_000_000)],
        'a_km3': [('a', 'km3', A, [OPP], 25_100_000_000)],
        'a_kx3': [('a', 'kx3', A, [OPP], 25_100_000_000)]}
KM3_LIMIT, KX3_NAME, KX3_STOP = 3000.0, 30000.0, 120000.0
P = OUTDIR / PLAN
P.mkdir(parents=True, exist_ok=True)
LOG = P / 'smoke.log'


def log(msg):
    line = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + ' ' + msg
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith(('KX_', 'PDL_', 'DECKGYM_', 'JEV_', 'PG_')) and k != 'TEST_CARD_SUPPORT_MISSING_ATTACK'}
    e.pop('RAYON_NUM_THREADS', None)   # as R6's self-checks: the pilot's own default (kx3's play-outs use rayon)
    if e.get('SMOKE_RAYON_THREADS'):
        e['RAYON_NUM_THREADS'] = e['SMOKE_RAYON_THREADS']
    return e


def manifest(run_dir, pilot, decks, opps, seed_base, deals=2, seats=(0, 1)):
    m = {'repo_root': str(ROOT), 'reference': 'km3', 'pilot': pilot, 'stage': 'smoke', 'log_level': 'full', 'threads': 1,
         'decks': [{'name': n, 'path': D + n + '.txt'} if not isinstance(n, tuple) else {'name': n[0], 'path': n[1]} for n in decks],
         'opponents': [{'name': n, 'path': p} for n, p in opps], 'deals': deals, 'seats': list(seats), 'seed_base': seed_base,
         'pair_stride': 10_000, 'heldout_decks': [], 'heldout_locked': True}
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / 'manifest.json').write_text(json.dumps(m, indent=1) + '\n')
    return run_dir / 'manifest.json'


def lines(p):
    return [json.loads(l) for l in open(p) if l.strip()] if p.exists() else []


def wait_pause():
    said = False
    while PAUSE.exists():
        if not said:
            log(f'paused: {PAUSE} exists')
        said = True
        time.sleep(60)
    if said:
        log('resumed')


def one_game(run_dir, mpath, max_games=1):
    """Plays the next game(s); returns (rc, to_play_before, stderr tail)."""
    cmd = ['nice', '-n', '19', str(PROGRAM), 'run', '--manifest', str(mpath), '--out', str(run_dir), '--threads', '1', '--max-games', str(max_games)]
    r = subprocess.run(cmd, env=env(), capture_output=True, text=True)
    with open(run_dir / 'strength.log', 'a') as f:
        f.write(r.stderr)
    todo = None
    for l in r.stderr.splitlines():
        if ' to play now' in l:
            todo = int(l.split(' already done, ')[1].split(' to play now')[0])
    return r.returncode, todo, r.stderr.strip()[-600:]


def seats_ms(g):
    """[(pilot, [ms...], [log entries...])] for the deck seat and the opponent seat."""
    return [(g['pilot_deck'], g['moves_deck']['ms'], g.get('log', [])), (g['pilot_opp'], g['moves_opp']['ms'], g.get('log_opp', []))]


def km3_max(g):
    return max([max(ms) for p, ms, _ in seats_ms(g) if p == 'km3' and ms] or [0.0])


def board(g, e):
    return (f"{g['key']} turn {e.get('t')} (own turn {e.get('o')}): {e.get('a')} of {e.get('n')} legal, {e.get('ms')} ms; points "
            f"{e.get('p')}, Active {e.get('act')}, Bench {e.get('b')}")


stop, kx3_stop, notes = [], [], []
for name, pilot, decks, opps, base in RUNS[PLAN]:
    rd = P / name
    mp = manifest(rd, pilot, decks, opps, base)
    log(f'{PLAN}/{name}: pilot {pilot} v km3, {len(decks)} deck(s) x {len(opps)} opponent(s) x 2 deals x 2 seats x 2 arms; program {PROGRAM}')
    while not stop and not kx3_stop:
        wait_pause()
        before = len(lines(rd / 'games.jsonl')); errs_before = len(lines(rd / 'errors.jsonl'))
        rc, todo, tail = one_game(rd, mp)
        if rc == 2:
            stop.append(f'{name}: refused (exit 2): {tail}'); break
        if rc != 0:
            stop.append(f'{name}: strength exit {rc}: {tail}'); break
        errs = lines(rd / 'errors.jsonl')
        if len(errs) > errs_before:
            stop.append(f'{name}: panic: {errs[-1]}'); break
        games = lines(rd / 'games.jsonl')
        if todo == 0 or len(games) == before:
            break
        g = games[-1]
        mx = km3_max(g)
        kx = [ms for p, msl, _ in seats_ms(g) if p.startswith('kx') for ms in msl]
        log(f"{g['key']}: {g['winner']} {g['points']} in {g['turns']} turns, {g['wall_s']} s; km3 max {mx:.1f} ms"
            + (f'; kx3 {len(kx)} decisions, max {max(kx):.1f} ms' if kx else ''))
        if mx > KM3_LIMIT:
            rr = rd / f"rerun_{g['key'].replace('|', '_')}"
            log(f"{g['key']}: a km3 decision over 3 s ({mx:.1f} ms): played again once in {rr.name}")
            m2 = manifest(rr, pilot, [(g['deck'], next(d['path'] for d in json.loads(mp.read_text())['decks'] if d['name'] == g['deck']))],
                          [(g['opp'], next(o['path'] for o in json.loads(mp.read_text())['opponents'] if o['name'] == g['opp']))],
                          g['seed'], deals=1, seats=(g['seat'],))
            rc2, _, tail2 = one_game(rr, m2, max_games=1 if g['arm'] == 'ref' else 2)
            again = [x for x in lines(rr / 'games.jsonl') if x['arm'] == g['arm']]
            if rc2 != 0 or not again:
                stop.append(f"{g['key']}: the re-run failed (exit {rc2}): {tail2}"); break
            mx2 = km3_max(again[-1])
            if mx2 > KM3_LIMIT:
                stop.append(f"{g['key']}: a km3 decision over 3 s twice ({mx:.1f} ms, then {mx2:.1f} ms)"); break
            notes.append(f"{g['key']}: km3 {mx:.1f} ms, re-run {mx2:.1f} ms (under 3 s): kept")
        over = [ms for ms in kx if ms > KX3_STOP]
        if over:
            kx3_stop.append(f"{g['key']}: a kx3 decision over 120 s ({max(over):.1f} ms)"); break

# the record, from every game played
rows, km3_all, kx3_all, slow = [], [], [], []
for name, pilot, decks, opps, base in RUNS[PLAN]:
    for g in lines(P / name / 'games.jsonl'):
        mx = km3_max(g)
        km3_all += [ms for p, msl, _ in seats_ms(g) if p == 'km3' for ms in msl]
        for p, msl, lg in seats_ms(g):
            if p.startswith('kx'):
                kx3_all += msl
                slow += ['kx3 over 30 s: ' + board(g, e) for e in lg if e.get('ms', 0) > KX3_NAME]
            if p == 'km3':
                slow += ['km3 over 3 s: ' + board(g, e) for e in lg if e.get('ms', 0) > KM3_LIMIT]
        rows.append([name, g['key'], g['arm'], g['pilot_deck'], g['pilot_opp'], g['winner'], json.dumps(g['points']), g['turns'], g['plies'],
                     g['wall_s'], g['moves_deck']['n'], g['moves_opp']['n'], f'{mx:.1f}', f"{max([0.0] + [m for p, ms, _ in seats_ms(g) if p.startswith('kx') for m in ms]):.1f}"])
    if PLAN.endswith('km3'):   # both arms are km3 v km3: they must be the same game
        gs = {(x['deck'], x['opp'], x['deal'], x['seat'], x['arm']): x for x in lines(P / name / 'games.jsonl')}
        for (d, o, dl, s, arm), x in gs.items():
            y = gs.get((d, o, dl, s, 'X' if arm == 'ref' else 'ref'))
            if arm == 'ref' and y and [x[k] for k in ('winner', 'points', 'turns', 'plies')] != [y[k] for k in ('winner', 'points', 'turns', 'plies')]:
                stop.append(f'{name}: km3 arms differ on {d}|{o}|{dl}|{s}')
if PLAN == 'a_kx3' and (OUTDIR / 'a_km3' / 'a' / 'games.jsonl').exists():
    base_g = {x['key']: x for x in lines(OUTDIR / 'a_km3' / 'a' / 'games.jsonl')}
    refs = [x for x in lines(P / 'a' / 'games.jsonl') if x['arm'] == 'ref']
    same = sum(1 for x in refs if x['key'] in base_g and [x[k] for k in ('winner', 'points', 'turns', 'plies')] == [base_g[x['key']][k] for k in ('winner', 'points', 'turns', 'plies')])
    notes.append(f"a_kx3's ref arm (km3 on K8's build) v a_km3's games (km3 on the lane build): {same} of {len(refs)} identical")
    if same != len(refs):
        stop.append(f"K8's km3 differs from the lane's km3 on {len(refs) - same} of {len(refs)} games")
with open(P / 'PER_GAME.tsv', 'w') as f:
    f.write('run\tkey\tarm\tpilot_deck\tpilot_opp\twinner\tpoints\tturns\tplies\twall_s\tdecisions_deck\tdecisions_opp\tkm3_max_ms\tkx3_max_ms\n')
    for r in rows:
        f.write('\t'.join(map(str, r)) + '\n')
(P / 'SLOW.tsv').write_text(''.join(s + '\n' for s in slow))
def stats(v):
    if not v:
        return 'none'
    s = sorted(v)
    return (f'{len(s)} decisions: mean {statistics.mean(s):.1f}, median {statistics.median(s):.1f}, '
            f'p95 {s[max(0, math.ceil(0.95 * len(s)) - 1)]:.1f}, max {s[-1]:.1f} ms')
panics = sum(len(lines(P / n / 'errors.jsonl')) for n, *_ in RUNS[PLAN])
out = [f'smoke {PLAN} (program {PROGRAM}, sha256 {subprocess.run(["sha256sum", str(PROGRAM)], capture_output=True, text=True).stdout[:64]})',
       f'games: {len(rows)} ({sum(1 for r in rows if r[2] == "X")} arm X, {sum(1 for r in rows if r[2] == "ref")} arm ref); panics {panics}; refusals {sum(1 for s in stop if "refused" in s)}',
       f'km3: {stats(km3_all)}', f'kx3: {stats(kx3_all)}'] + [f'note: {n}' for n in notes] + [f'slow: {s}' for s in slow[:60]]
verdict = ('STOP: ' + '; '.join(stop)) if stop else (('KX3_STOP: ' + '; '.join(kx3_stop)) if kx3_stop else 'OK')
out.append(f'SMOKE {PLAN} {verdict}')
(P / 'SUMMARY.txt').write_text('\n'.join(out) + '\n')
for l in out:
    log(l)
sys.exit(1 if stop else (3 if kx3_stop else 0))
