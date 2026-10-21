#!/usr/bin/env python3
"""Play one legality_scan command with the OLD pinned program (programs/O) and the candidate (programs/N), then compare the
candidate's games with the old program's on every field (switch_check.py same). For rows the old pin never recorded.
  oldnew.py LABEL --from-run NAME            the args of rl/results/engine_switch_rules2_2026-10/NAME.run (paths mapped)
  oldnew.py LABEL --args '<legality_scan args>'
Output games/oldnew/LABEL_{old,new}.{jsonl,txt}, LABEL.cmp, LABEL.diff.tsv; a line in games/summary.tsv (side 'oldnew')."""
import os, shlex, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, '/home/dacz8976/pincand_work')
from replay import diff_jsonl  # noqa: E402

W = Path('/home/dacz8976/pincand_work')
R = Path('/home/dacz8976/pincand')
SW2 = R / 'rl/results/engine_switch_rules2_2026-10'
WIN = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
OLD_CWD = '/home/dacz8976/engine-rules2-08a9b3a/engine'
label = sys.argv[1]
if sys.argv[2] == '--from-run':
    lines = (SW2 / f'{sys.argv[3]}.run').read_text().splitlines()
    raw = shlex.split(next(l[5:] for l in lines if l.startswith('args ')))
else:
    raw = shlex.split(sys.argv[3])
out = W / 'games/oldnew'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, RAYON_NUM_THREADS='8')
env.pop('PDL_DB', None)
if any(k.startswith('DECKGYM_') for k in env):
    sys.exit('DECKGYM_* set: refusing')
t0 = time.time()
files = {}
for side, arch, prog in (('old', W / 'O', W / 'programs/O/legality_scan'), ('new', W / 'N', W / 'programs/N/legality_scan')):
    args = [a.replace(OLD_CWD, str(arch / 'engine')).replace(WIN, str(R)) for a in raw]
    f = out / f'{label}_{side}.jsonl'
    cmd = ['nice', '-n', '19', 'ionice', '-c3', str(prog)] + args + ['--games-out', str(f)]
    (out / f'{label}_{side}.cmd').write_text(f'cwd {arch / "engine"}\n' + ' '.join(shlex.quote(c) for c in cmd) + '\n')
    if not f.exists():
        with open(out / f'{label}_{side}.txt', 'w') as log:
            rc = subprocess.run(cmd, cwd=arch / 'engine', env=env, stdout=log, stderr=subprocess.STDOUT).returncode
        if rc != 0:
            with open(W / 'games/summary.tsv', 'a') as s:
                s.write(f'oldnew\t{label}\t0\t{int(time.time() - t0)}\tERROR\t{side} exit {rc}\n')
            sys.exit(1)
    files[side] = f
n = sum(1 for _ in open(files['old']))
chk = subprocess.run(['python3', str(SW2 / 'switch_check.py'), 'same', str(files['new']), '--ref', str(files['old']), '--expect', str(n),
                      '--label', f'new v old {label}'], capture_output=True, text=True)
(out / f'{label}.cmp').write_text(chk.stdout + chk.stderr)
nd, na, nb = diff_jsonl(files['new'], files['old'], out / f'{label}.diff.tsv')
verdict = 'SAME' if chk.returncode == 0 else ('DIFFERS' if chk.returncode == 1 else 'ERROR')
with open(W / 'games/summary.tsv', 'a') as s:
    s.write(f'oldnew\t{label}\t{na}\t{int(time.time() - t0)}\t{verdict}\t{nd} differing deals of {nb} (new v old, both played tonight)\n')
print(label, verdict, nd, flush=True)
