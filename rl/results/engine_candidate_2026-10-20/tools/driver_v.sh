#!/bin/bash
# V = the candidate WITHOUT the #401 commit (42d2dd8e reverted; local ref only). legality_scan only. Then the d_rayquaza rows
# (Skull Fossil) for km3, kta3, k3 on V, and U (no Growl) on pairing 3 (v research/lucario, the one Growl-reachable pairing).
set -u
W=/home/dacz8976/pincand_work
R=/home/dacz8976/pincand
C=d9d2e70458273b77c379a7424ad33a162289205a
mkdir -p $W/pgids $W/games/v
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/v.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $W/driver.log; }
export CARGO_BUILD_JOBS=2
G="nice -n 19 ionice -c3"
pgrep -x cargo >/dev/null && { log "driver_v: a cargo is running; stop"; exit 1; }
cd $R
python3 - <<'EOF' > $W/games/v/dray_pairings.txt
import collections
for b in ('km3', 'kta3', 'k3'):
    rows = [l.split('\t') for l in open(f'/home/dacz8976/pincand_work/games/oldnew/dray_dev_{b}.diff.tsv').read().splitlines()[1:] if l]
    c = collections.Counter(int(r[0]) for r in rows)
    flips = sum(1 for r in rows if r[5] != r[6])
    print(b, len(rows), 'by pairing', dict(sorted(c.items())), 'winner flips', flips)
EOF
cat $W/games/v/dray_pairings.txt | tee -a $W/driver.log
if [ ! -e $W/build_V.done ]; then
  F401=$(git log --format=%H --grep='upstream #401' $C -1)
  rm -rf $W/V $W/Vgit && mkdir -p $W/V
  git worktree add -q --detach $W/Vgit $C
  git -C $W/Vgit -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com revert --no-edit $F401 > /dev/null
  VC=$(git -C $W/Vgit rev-parse HEAD)
  git update-ref refs/pocketdecksim/engine-candidate-2026-10-20-V $VC
  log "V = $VC: $C with the #401 commit $F401 reverted (local ref refs/pocketdecksim/engine-candidate-2026-10-20-V); diff v candidate: $(git diff --stat $C $VC -- engine | tail -1)"
  git -c core.autocrlf=false archive $VC engine decks | tar -x -C $W/V
  git worktree remove --force $W/Vgit
  find $W/V -type f -exec touch {} +
  ( cd $W/V/engine && unset CARGO_TARGET_DIR && s=$(date +%s) && $G cargo build --release --locked --example legality_scan && echo "BUILD OK in $(( $(date +%s) - s )) s" ) > $W/build_V.log 2>&1
  grep -q 'BUILD OK' $W/build_V.log || { log "build_V FAILED"; exit 1; }
  mkdir -p $W/programs/V && cp $W/V/engine/target/release/examples/legality_scan $W/programs/V/
  log "build_V OK: $(tail -1 $W/build_V.log); legality_scan $(sha256sum $W/programs/V/legality_scan | cut -c1-64)"
  date -u +%FT%TZ > $W/build_V.done
fi
CK=$R/rl/results/engine_switch_rules2_2026-10/switch_check.py
P=/home/dacz8976/pincand/rl/results/kta_tables_2026-09-29/pairs/dev_d_rayquaza.tsv
for bot in km3 kta3 k3; do
  f=$W/games/v/dray_dev_${bot}_V.jsonl
  [ -s $f ] || ( cd $W/V/engine && RAYON_NUM_THREADS=8 $G $W/programs/V/legality_scan --pairs $P --root $R --seed-base 22700000000 --bot $bot --pairings 0,1,2,3,4,5,6,7 --games 500 --games-out $f > ${f%.jsonl}.txt 2>&1 )
  python3 $CK same $f --ref $W/games/oldnew/dray_dev_${bot}_old.jsonl --expect 4000 --exclude-pairings 3 --label "V v old dray $bot (pairings other than 3)" > ${f%.jsonl}.cmp 2>&1
  log "V v old, dray $bot, pairings 0-2,4-7: exit $? $(tail -1 ${f%.jsonl}.cmp | cut -c1-160)"
  python3 $CK same $f --ref $W/games/oldnew/dray_dev_${bot}_old.jsonl --expect 500 --pairings 3 --label "V v old dray $bot pairing 3" > ${f%.jsonl}_p3.cmp 2>&1
  log "V v old, dray $bot, pairing 3: exit $? $(tail -1 ${f%.jsonl}_p3.cmp | cut -c1-160)"
  u=$W/games/v/dray_dev_${bot}_U_p3.jsonl
  [ -s $u ] || ( cd $W/U/engine && RAYON_NUM_THREADS=8 $G $W/programs/U/legality_scan --pairs $P --root $R --seed-base 22700000000 --bot $bot --pairings 3 --games 500 --games-out $u > ${u%.jsonl}.txt 2>&1 )
  python3 $CK same $u --ref $W/games/oldnew/dray_dev_${bot}_new.jsonl --expect 500 --pairings 3 --label "U v new dray $bot pairing 3" > ${u%.jsonl}_vnew.cmp 2>&1
  log "U v new (candidate), dray $bot pairing 3: exit $? $(tail -1 ${u%.jsonl}_vnew.cmp | cut -c1-160)"
  python3 $CK same $u --ref $W/games/oldnew/dray_dev_${bot}_old.jsonl --expect 500 --pairings 3 --label "U v old dray $bot pairing 3" > ${u%.jsonl}_vold.cmp 2>&1
  log "U v old, dray $bot pairing 3: exit $? $(tail -1 ${u%.jsonl}_vold.cmp | cut -c1-160)"
done
date -u +%FT%TZ > $W/v.done
log "driver_v done"
