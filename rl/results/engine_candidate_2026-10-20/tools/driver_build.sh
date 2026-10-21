#!/bin/bash
# Engine candidate, night driver 1: build the candidate's programs, run the engine suite, build the strength harness, run the km3
# self-checks (old and new). Gentle: CARGO_BUILD_JOBS 2, nice 19, ionice -c3, one cargo at a time. Resumable: each step leaves a .done.
set -u
W=/home/dacz8976/pincand_work
REPO=/home/dacz8976/pincand
C=${C:-d9d2e70458273b77c379a7424ad33a162289205a}
N=$W/N
P=$W/programs/N
LOG=$W/driver.log
mkdir -p $W $P
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/driver.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
done_() { [ -e "$W/$1.done" ]; }
mark() { date -u +%FT%TZ > "$W/$1.done"; }
export CARGO_BUILD_JOBS=2
G="nice -n 19 ionice -c3"
log "driver_build start; candidate $C (engine tree $(git -C $REPO rev-parse $C:engine))"

if ! done_ build_N; then
  log "build_N: archive + cargo build --release --locked (deckgym, legality_scan, goldfish), jobs 2"
  rm -rf $N && mkdir -p $N
  git -C $REPO -c core.autocrlf=false archive $C engine decks | tar -x -C $N
  find $N -type f -exec touch {} +
  ( cd $N/engine && unset CARGO_TARGET_DIR && s=$(date +%s) &&
    $G cargo build --release --locked && $G cargo build --release --locked --example legality_scan &&
    $G cargo build --release --locked --example goldfish && echo "BUILD OK in $(( $(date +%s) - s )) s" ) > $W/build_N.log 2>&1
  if ! grep -q 'BUILD OK' $W/build_N.log; then log "build_N FAILED"; grep -E '^error' -A12 $W/build_N.log | head -60 | tee -a $LOG; exit 1; fi
  cp $N/engine/target/release/deckgym $N/engine/target/release/examples/legality_scan $N/engine/target/release/examples/goldfish $P/
  ( cd $P && sha256sum deckgym legality_scan goldfish > SHA256SUMS )
  log "build_N OK: $(tail -1 $W/build_N.log); $(tr '\n' ' ' < $P/SHA256SUMS)"
  mark build_N
fi

if ! done_ test_N1; then
  log "test_N1: cargo test --release --features test-utils --locked --no-fail-fast (RUST_TEST_THREADS 2)"
  s=$(date +%s)
  ( cd $N/engine && unset CARGO_TARGET_DIR && RUST_TEST_THREADS=2 $G cargo test --release --features test-utils --locked --no-fail-fast ) > $W/test_N1.log 2>&1
  rc=$?
  python3 - $W/test_N1.log <<'EOF' | tee -a $LOG
import re, sys
t = open(sys.argv[1], errors='replace').read()
p = sum(int(x) for x in re.findall(r'test result: \w+\. (\d+) passed', t))
f = sum(int(x) for x in re.findall(r'(\d+) failed', ' '.join(re.findall(r'test result: [^\n]*', t))))
fails = sorted(set(re.findall(r'^---- (\S+)', t, re.M)))
print(f"test_N1: {p} passed, {f} failed; failing: {fails[:40]}")
EOF
  log "test_N1 rc=$rc in $(( $(date +%s) - s )) s"
  mark test_N1
fi

if ! done_ strength_N; then
  log "strength_N: rl/strength/build.sh $C -> $P/strength (own build and target folders)"
  ( cd $REPO && STRENGTH_REPO=$REPO STRENGTH_BUILD_DIR=$W/strength_build STRENGTH_TARGET_DIR=$W/strength_target \
      bash rl/strength/build.sh $C $P/strength ) > $W/strength_N.log 2>&1 || { log "strength_N FAILED"; tail -20 $W/strength_N.log | tee -a $LOG; exit 1; }
  log "strength_N OK: $(sha256sum $P/strength | cut -c1-64)"
  mark strength_N
fi

if ! done_ selfcheck_km3; then
  cd $REPO
  for side in old new; do
    if [ $side = old ]; then prog=/home/dacz8976/kx_r2/strength; else prog=$P/strength; fi
    line=$($G $prog selfcheck --pilot km3 --deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12 2>&1 | tail -1)
    log "selfcheck km3 $side ($(sha256sum $prog | cut -c1-16)): $line"
    echo "$side $(sha256sum $prog | cut -c1-64) $line" >> $W/selfcheck_km3.txt
  done
  mark selfcheck_km3
fi
log "driver_build done"
