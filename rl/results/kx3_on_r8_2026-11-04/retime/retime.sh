#!/bin/bash
# coordinator-157 (1): a quiet re-time of one key's game (01 v t-hydreigon, deal 0, seat 0; the kx3 arm, with its km3 twin) on K8 and on
# R6's pinned program, in the order K8, R6, K8, R6, alone, nice 19 + ionice, 1 thread; waits while PAUSE exists. Nothing is committed.
set -u
O=/home/dacz8976/relplan/r8/retime; rm -rf $O; mkdir -p $O
WT=/home/dacz8976/r5_w; D=$WT/rl/results/kx3_on_r8_2026-11-04
K8=/home/dacz8976/pincand_work/RR_R8_48dec4f5/strength/K8/strength; R6=/home/dacz8976/kx_r4/strength
PAUSE=/home/dacz8976/credit_work/PAUSE
SCRUB=$(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)' | sed 's/^/-u /' | tr '\n' ' ')
[ "$(sha256sum < $K8 | cut -c1-16)" = d4d4e43acebcf7ae ] && [ "$(sha256sum < $R6 | cut -c1-16)" = 23d8a9b5a2e70f06 ] || { echo "STOP: program sha"; exit 1; }
# one-key manifest from replay_b's (deck 01 is replay_b's), seed_base = the key's own seed in the dev run
python3 -I - $D/replay_b/manifest.json $WT/rl/results/strength_2026-10-03_kx3_dev/games.jsonl $O <<'EOF'
import json, sys
mp, dg, out = sys.argv[1:]
m = json.load(open(mp))
d = [x for x in m['decks'] if x['name'] == '01-muk-glimmora-kingambit-regigigas']; o = [x for x in m['opponents'] if x['name'] == 't-hydreigon']
assert len(d) == 1 and len(o) == 1
seeds = {(g['deck'], g['opp'], g['deal'], g['seat'], g['arm']): g['seed'] for g in map(json.loads, (l for l in open(dg) if l.strip().endswith('}')))}
s = seeds[('01-muk-glimmora-kingambit-regigigas', 't-hydreigon', 0, 0, 'X')]
assert s == seeds[('01-muk-glimmora-kingambit-regigigas', 't-hydreigon', 0, 0, 'ref')]
for prog, sha in (('K8', m['program_sha256']), ('R6', '23d8a9b5a2e70f06abc4b6989c6662e73c5ebc33baecbe9727e1af1c4f413378')):
    mm = dict(m, decks=d, opponents=o, deals=1, seats=[0], seed_base=s, name=f'retime_{prog}', program_sha256=sha)
    json.dump(mm, open(f'{out}/manifest_{prog}.json', 'w'), indent=1)
print('seed', s)
EOF
cd $WT
for step in 1:K8 2:R6 3:K8 4:R6; do
  i=${step%%:*}; p=${step#*:}; P=$([ $p = K8 ] && echo $K8 || echo $R6)
  while [ -e $PAUSE ]; do sleep 60; done
  mkdir -p $O/run$i
  s=$(date +%s)
  env $SCRUB nice -n 19 ionice -c3 $P run --manifest $O/manifest_$p.json --out $O/run$i --threads 1 > $O/run$i.log 2>&1; rc=$?
  echo "run $i ($p): rc $rc, $(( $(date +%s) - s )) s wall, $(date -u +%FT%TZ)" | tee -a $O/RUNS.txt
done
cd $WT/rl/strength && python3 -I - $O $WT/rl/results/strength_2026-10-03_kx3_dev/games.jsonl <<'EOF' | tee $O/RETIME.txt
import json, sys
sys.path.insert(0, '.')
from split_collect import content
out, dg = sys.argv[1:]
key = ('01-muk-glimmora-kingambit-regigigas', 't-hydreigon', 0, 0, 'X')
dev = next(g for g in map(json.loads, (l for l in open(dg) if l.strip().endswith('}'))) if (g['deck'], g['opp'], g['deal'], g['seat'], g['arm']) == key)
res = {}
for i, p in ((1, 'K8'), (2, 'R6'), (3, 'K8'), (4, 'R6')):
    g = next(g for g in map(json.loads, (l for l in open(f'{out}/run{i}/games.jsonl') if l.strip().endswith('}'))) if g['arm'] == 'X')
    ms = [e['ms'] for e in g['log'] if e.get('ms') is not None]
    eq = content(g) == content(dev)
    res.setdefault(p, []).append(ms[3])
    print(f'run {i} ({p}): decision #3 (0-based index 3, {g["log"][3].get("a")}) {ms[3]:,.1f} ms; game total kx3 {sum(ms):,.0f} ms over {len(ms)} decisions; equals the dev run: {eq}')
k8, r6 = sum(res['K8']) / 2, sum(res['R6']) / 2
print(f'mean decision #3: K8 {k8:,.1f} ms, R6 {r6:,.1f} ms, ratio {k8 / r6:.3f} ("not much slower" means at most 1.3)')
EOF
