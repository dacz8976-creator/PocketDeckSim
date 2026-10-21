#!/bin/bash
# Engine candidate, night driver 3 (beside the games, gentle: CARGO_BUILD_JOBS 1, nice 19, ionice -c3, one cargo at a time):
#  1. test_N2: the ported upstream tests (uncommitted files in the pincand working tree, copied into the N archive's tests/)
#  2. kx3 on the candidate: laptop/kx3-on-rules2's added player files laid over the candidate engine, built with rl/strength/build.sh
#  3. the kx3 self-check (recorded 31d638dbc818b0fa on the slow-report pin's program 76df495b)
set -u
W=/home/dacz8976/pincand_work
R=/home/dacz8976/pincand
C=d9d2e70458273b77c379a7424ad33a162289205a
LOG=$W/driver.log
mkdir -p $W/pgids
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/extra.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
done_() { [ -e "$W/$1.done" ]; }
mark() { date -u +%FT%TZ > "$W/$1.done"; }
export CARGO_BUILD_JOBS=1
G="nice -n 19 ionice -c3"
pgrep -x cargo >/dev/null && { log "driver_extra: a cargo is running; stop"; exit 1; }

if ! done_ test_N2; then
  log "test_N2: the ported tests (git status in pincand: $(git -C $R status --porcelain engine | wc -l) paths) copied into N/engine/tests; cargo test, jobs 1"
  git -C $R status --porcelain engine > $W/test_N2_files.txt
  ( cd $R && git status --porcelain engine | awk '{print $2}' | while read -r p; do mkdir -p "$W/N/$(dirname "$p")"; cp "$p" "$W/N/$p"; done )
  s=$(date +%s)
  ( cd $W/N/engine && unset CARGO_TARGET_DIR && RUST_TEST_THREADS=1 $G cargo test --release --features test-utils --locked --no-fail-fast ) > $W/test_N2.log 2>&1
  rc=$?
  python3 - $W/test_N2.log <<'EOF' | tee -a $LOG
import re, sys
t = open(sys.argv[1], errors='replace').read()
p = sum(int(x) for x in re.findall(r'test result: \w+\. (\d+) passed', t))
f = sum(int(x) for x in re.findall(r'(\d+) failed', ' '.join(re.findall(r'test result: [^\n]*', t))))
fails = sorted(set(re.findall(r'^---- (\S+)', t, re.M)))
errs = re.findall(r'^error(?:\[E\d+\])?: .*', t, re.M)
print(f"test_N2: {p} passed, {f} failed; failing: {fails[:40]}; compile errors: {len(errs)} {errs[:5]}")
EOF
  log "test_N2 rc=$rc in $(( $(date +%s) - s )) s"
  mark test_N2
fi

if ! done_ strength_K; then
  log "strength_K: candidate engine + kx3's added files (laptop/kx3-on-rules2 cd20a97a)"
  git -C $R fetch -q origin laptop/kx3-on-rules2
  KB=$(git -C $R merge-base origin/main cd20a97a)
  git -C $R diff --stat $KB cd20a97a -- engine | tail -8 >> $LOG
  rm -rf $W/K && mkdir -p $W/K
  git -C $R -c core.autocrlf=false archive $C engine | tar -x -C $W/K
  git -C $R diff --binary $KB cd20a97a -- engine > $W/kx3_overlay.patch
  ( cd $W/K && git apply --whitespace=nowarn $W/kx3_overlay.patch ) >> $LOG 2>&1 || { log "kx3 overlay did not apply: stop"; exit 1; }
  ( cd $R && STRENGTH_REPO=$R STRENGTH_BUILD_DIR=$W/strength_build_K STRENGTH_TARGET_DIR=$W/strength_target_K \
      bash rl/strength/build.sh $W/K/engine $W/programs/N/strength_kx3 ) > $W/strength_K.log 2>&1 || { log "strength_K FAILED"; tail -20 $W/strength_K.log | tee -a $LOG; exit 1; }
  log "strength_K OK: $(sha256sum $W/programs/N/strength_kx3 | cut -c1-64) (overlay base $KB)"
  mark strength_K
fi

if ! done_ selfcheck_kx3; then
  cd $R
  s=$(date +%s)
  line=$($G $W/programs/N/strength_kx3 selfcheck --pilot kx3 --deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12 2>&1 | tail -1)
  log "selfcheck kx3 new ($(sha256sum $W/programs/N/strength_kx3 | cut -c1-16)) in $(( $(date +%s) - s )) s: $line"
  echo "new $(sha256sum $W/programs/N/strength_kx3 | cut -c1-64) $line" >> $W/selfcheck_kx3.txt
  line=$($G $W/programs/N/strength_kx3 selfcheck --pilot km3 --deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12 2>&1 | tail -1)
  log "selfcheck km3 on the kx3 build: $line"
  mark selfcheck_kx3
fi
log "driver_extra done"
