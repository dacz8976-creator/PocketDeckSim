#!/bin/bash
# The refusal test's own program (test_strength_card_support.py:8-12): the release tip's harness + engine, WITH deckgym/test-utils.
# Only for the refusal test; never a slow-report or sc_ program.
set -u
SWT=/home/dacz8976/lane_r8_w; N=/home/dacz8976/pincand_work/RR_R8_543dad00/sw3; B=$N/tu_build
[ -e /home/dacz8976/credit_work/PAUSE ] && { echo "PAUSE present"; exit 1; }
pgrep -x cargo >/dev/null && { echo "STOP: another cargo is running"; exit 1; }
[ -e $B ] && { echo "STOP: $B exists"; exit 1; }
SCRUB=$(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_|CARGO_TARGET)' | sed 's/^/-u /' | tr '\n' ' ')
cd $SWT || exit 1
mkdir -p $B/rl/strength && cp -r engine $B/ && cp -r rl/strength/src rl/strength/Cargo.toml $B/rl/strength/ && cp engine/Cargo.lock $B/rl/strength/
s=$(date +%s)
( cd $B/rl/strength && env $SCRUB CARGO_BUILD_JOBS=2 nice -n 19 ionice -c3 cargo build --release --offline --features deckgym/test-utils ) > $N/tu_build.log 2>&1
rc=$?; echo "build rc=$rc in $(( $(date +%s) - s )) s"; tail -n 3 $N/tu_build.log
PT=$B/rl/strength/target/release/strength
[ $rc = 0 ] && [ -x $PT ] || exit 1
echo "program sha256 $(sha256sum < $PT | cut -c1-64)"
( cd $SWT/rl/strength && env $SCRUB STRENGTH_PROGRAM=$PT nice -n 19 python3 -B -m unittest -v test_strength_card_support ) > $N/strength_refusal_tu.log 2>&1
echo "refusal (test-utils program): rc=$? $(grep -E '^(Ran|OK|FAILED)' $N/strength_refusal_tu.log | tr '\n' ' ')"
