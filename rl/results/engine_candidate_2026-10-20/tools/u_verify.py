#!/usr/bin/env python3
"""For every candidate run that DIFFERS from the old pin: replay exactly its changed pairings on U (the candidate without the
Growl commit) with the recorded command, and compare U with the old pin's reference on those pairings.
  U == old on those pairings  -> every candidate change there comes from the Growl commit: group (a) when a cut card is in a deck
  U != old                    -> the change comes from the upstream items (b) or is unexplained (c): listed with its deals
Writes games/u/verify.tsv: run, pairings, deals, U_v_old (SAME|DIFFERS|ERROR), detail."""
import os, re, shlex, subprocess, time
from pathlib import Path

W = Path('/home/dacz8976/pincand_work')
R = Path('/home/dacz8976/pincand')
SW2 = R / 'rl/results/engine_switch_rules2_2026-10'
WIN = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
OLD_CWD = '/home/dacz8976/engine-rules2-08a9b3a/engine'
U = W / 'U'
out = W / 'games/u'
out.mkdir(parents=True, exist_ok=True)
rows = []
for line in (W / 'games/summary.tsv').read_text().splitlines():
    c = line.split('\t')
    if c[0] == 'new' and c[4] == 'DIFFERS' and (W / f'games/new/{c[1]}.diff.tsv').exists():
        rows.append(c[1])
res = open(out / 'verify.tsv', 'a')
for name in dict.fromkeys(rows):
    diff = [l.split('\t') for l in (W / f'games/new/{name}.diff.tsv').read_text().splitlines()[1:] if l]
    pairings = sorted({int(d[0]) for d in diff})
    plist = ','.join(map(str, pairings))
    lines = (SW2 / f'{name}.run').read_text().splitlines()
    args = shlex.split(next(l[5:] for l in lines if l.startswith('args ')))
    args = [a.replace(OLD_CWD, str(U / 'engine')).replace(WIN, str(R)) for a in args]
    k = args.index('--pairings')
    args[k + 1] = plist
    games = int(args[args.index('--games') + 1])
    f = out / f'{name}_p{plist.replace(",", "_")}.jsonl'
    env = dict(os.environ, RAYON_NUM_THREADS='8')
    env.pop('PDL_DB', None)
    if any(x.startswith('DECKGYM_') for x in env):
        raise SystemExit('DECKGYM_* set: refusing')
    t0 = time.time()
    if not f.exists():
        with open(f.with_suffix('.txt'), 'w') as log:
            rc = subprocess.run(['nice', '-n', '19', 'ionice', '-c3', str(W / 'programs/U/legality_scan')] + args + ['--games-out', str(f)],
                                cwd=U / 'engine', env=env, stdout=log, stderr=subprocess.STDOUT).returncode
        if rc != 0:
            res.write(f'{name}\t{plist}\t{len(diff)}\tERROR\texit {rc}\n'); res.flush(); continue
    chk = subprocess.run(['python3', str(SW2 / 'switch_check.py'), 'same', str(f), '--ref', str(SW2 / f'{name}.jsonl'), '--pairings', plist,
                          '--expect', str(games * len(pairings)), '--label', f'U v old {name} p{plist}'], capture_output=True, text=True)
    (out / f'{name}_p{plist.replace(",", "_")}.cmp').write_text(chk.stdout + chk.stderr)
    verdict = 'SAME' if chk.returncode == 0 else ('DIFFERS' if chk.returncode == 1 else 'ERROR')
    res.write(f'{name}\t{plist}\t{len(diff)}\t{verdict}\t{int(time.time() - t0)} s; {chk.stdout.strip().splitlines()[-1][:200] if chk.stdout.strip() else chk.stderr.strip()[:200]}\n')
    res.flush()
    print(name, plist, verdict, flush=True)
res.close()
