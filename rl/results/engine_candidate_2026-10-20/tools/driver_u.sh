#!/bin/bash
# U = the candidate WITHOUT the Growl commit (501fc1dd reverted on a local-only ref). Builds legality_scan only, then plays the
# new17 pairings 21 and 22 (the g-mega_altaria_greninja cells the PLAN named) for k3, kp3 and km3 with the recorded command's
# seeds, and compares: U v the old pin's reference (expect SAME: then every N change there comes from the Growl commit).
set -u
W=/home/dacz8976/pincand_work
R=/home/dacz8976/pincand
C=d9d2e70458273b77c379a7424ad33a162289205a
LOG=$W/driver.log
mkdir -p $W/pgids $W/games/u
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/u.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
export CARGO_BUILD_JOBS=2
G="nice -n 19 ionice -c3"
pgrep -x cargo >/dev/null && { log "driver_u: a cargo is running; stop"; exit 1; }
if [ ! -e $W/build_U.done ]; then
  GROWL=$(git -C $R log --format=%H --grep='an attack cut to 0 by an attacker-side effect does 0' $C -1)
  rm -rf $W/U $W/Ugit && mkdir -p $W/U
  git -C $R worktree add -q --detach $W/Ugit $C
  git -C $W/Ugit -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com revert --no-edit $GROWL > /dev/null
  UC=$(git -C $W/Ugit rev-parse HEAD)
  git -C $R update-ref refs/pocketdecksim/engine-candidate-2026-10-20-U $UC
  log "U = $UC: $C with the Growl commit $GROWL reverted (local ref refs/pocketdecksim/engine-candidate-2026-10-20-U; not pushed); engine diff v the candidate: $(git -C $R diff --stat $C $UC -- engine | tail -1)"
  git -C $R -c core.autocrlf=false archive $UC engine decks | tar -x -C $W/U
  git -C $R worktree remove --force $W/Ugit
  find $W/U -type f -exec touch {} +
  ( cd $W/U/engine && unset CARGO_TARGET_DIR && s=$(date +%s) && $G cargo build --release --locked --example legality_scan && echo "BUILD OK in $(( $(date +%s) - s )) s" ) > $W/build_U.log 2>&1
  grep -q 'BUILD OK' $W/build_U.log || { log "build_U FAILED"; grep -E '^error' -A8 $W/build_U.log | head -30 | tee -a $LOG; exit 1; }
  mkdir -p $W/programs/U && cp $W/U/engine/target/release/examples/legality_scan $W/programs/U/
  log "build_U OK: $(tail -1 $W/build_U.log); legality_scan $(sha256sum $W/programs/U/legality_scan | cut -c1-64)"
  date -u +%FT%TZ > $W/build_U.done
fi
SW2=$R/rl/results/engine_switch_rules2_2026-10
CK=$SW2/switch_check.py
for name in 08a9b3a_new17_k3 08a9b3a_new17_kp3 08a9b3a_dev_km3_new17; do
  out=$W/games/u/${name}_p21_22.jsonl
  if [ ! -s $out ]; then
    args=$(grep '^args ' $SW2/$name.run | cut -c6- | sed "s#/mnt/c/Users/dacz8/Projects/Pocket\\\\ Deck\\\\ Sim/PocketDeckSim#$R#g" | sed -E 's/--pairings [0-9\\,]+/--pairings 21,22/')
    s=$(date +%s)
    ( cd $W/U/engine && eval "RAYON_NUM_THREADS=8 $G $W/programs/U/legality_scan $args --games-out $out" ) > $W/games/u/${name}_p21_22.txt 2>&1 || log "U $name: exit $?"
    log "U $name pairings 21,22: $(wc -l < $out) games in $(( $(date +%s) - s )) s"
  fi
  python3 $CK same $out --ref $SW2/$name.jsonl --pairings 21,22 --expect 1000 --label "U v old $name p21-22" > $W/games/u/${name}_p21_22.cmp 2>&1
  log "U v old ($name, pairings 21-22): exit $? $(tail -1 $W/games/u/${name}_p21_22.cmp | cut -c1-200)"
done
log "driver_u done"
