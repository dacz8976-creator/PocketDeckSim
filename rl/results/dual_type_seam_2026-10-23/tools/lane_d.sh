#!/bin/bash
# Dual Fusion step 1 (coordinator GO, Oct 23): the night lane for the dual-type seam branch. Night window only
# (02:00-12:50Z; the keeper pinkeep freezes this process group at 12:55Z). CARGO_BUILD_JOBS 2, STRENGTH_JOBS 2, nice 19,
# ionice -c3, one cargo at a time. Each step marks $R/<step>.done; a re-run skips done steps.
#   1. build_D: the three programs from the seam worktree at D_COMMIT (clean tree, persistent target dir) -> programs/D.
#   2. gen_D:   card_enum_generator re-run; its database.rs and card_ids.rs output must equal the committed files.
#   3. suite_D: the whole suite (cargo test --release --features test-utils --no-fail-fast).
#   4. ref_F:   side f (main-4d48844) for the A5 tables it lacks (kp3, kog3, kta3), so every d run has an f twin.
#   5. replays_D: side d (the seam) on the A5 rows and more, each compared game for game with side f.
# A failed build or suite stops the lane (end marker written); the laptop session fixes and re-arms.
set -u
S=/home/dacz8976/pincand_work/hb
W=/home/dacz8976/pincand_work
WT=/home/dacz8976/dual_w
R=$W/dual
TGT=/home/dacz8976/dual_target
REF_F="08a9b3a_table_kp3 08a9b3a_table_kog3 08a9b3a_dev_kta3_table"
REPLAYS="08a9b3a_10_cli_k3 08a9b3a_10_cli_kp3 08a9b3a_10_cli_kog3 08a9b3a_10_cli_kta3 08a9b3a_10_cli_km3 08a9b3a_10_goldfish 08a9b3a_table_k3 08a9b3a_table_kp3 08a9b3a_table_kog3 08a9b3a_dev_km3_table 08a9b3a_dev_kta3_table 08a9b3a_10_run_screen 08a9b3a_new17_k3 08a9b3a_dev_km3_new17 08a9b3a_8b_cloud_new_k3 08a9b3a_8b_cloud_new_km3 08a9b3a_8_new_km3 08a9b3a_cov_b2e_km3"
LOG=$R/lane_d.log
mkdir -p $R $W/pgids
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/lane_d.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
done_() { [ -e "$R/$1.done" ]; }
mark() { date -u +%FT%TZ > "$R/$1.done"; rm -f "$R/$1.FAILED"; }
fail() { echo "$(date -u +%FT%TZ) $2" > "$R/$1.FAILED"; log "$1 FAILED: $2"; }
finish() { log "lane_d end: $1"; date -u +%FT%TZ > $R/lane_d.end; exit 0; }
# the night window, or earlier when Dustin releases the laptop ($W/RELEASE_UNTIL: an epoch second, at most the next 12:50Z)
in_window() { local m=$((10#$(date -u +%H) * 60 + 10#$(date -u +%M))); { [ $m -ge 120 ] && [ $m -lt 770 ]; } || [ "$(date +%s)" -lt "$(cat $W/RELEASE_UNTIL 2>/dev/null || echo 0)" ]; }
wait_window() { while ! in_window; do sleep 60; done; }
no_cargo() { while pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null; do log "waiting: another cargo/rustc is running"; sleep 120; done; }
export CARGO_BUILD_JOBS=2 STRENGTH_JOBS=2 CARGO_TARGET_DIR=$TGT
for v in $(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)'); do unset "$v"; done
G="nice -n 19 ionice -c3"
rm -f $R/lane_d.end
log "lane_d armed (pgid $(cat $W/pgids/lane_d.pgid))"
wait_window
[ -s $R/D_COMMIT ] || { fail lane_d "no $R/D_COMMIT"; finish "no commit"; }
D=$(git -C $WT rev-parse "$(cat $R/D_COMMIT)^{commit}") || { fail lane_d "bad D_COMMIT"; finish "bad commit"; }
[ "$(git -C $WT rev-parse HEAD)" = "$D" ] || { fail lane_d "worktree HEAD is not D_COMMIT"; finish "HEAD moved"; }
[ -z "$(git -C $WT status --porcelain --untracked-files=no)" ] || { fail lane_d "worktree has uncommitted changes"; finish "dirty"; }
log "lane_d start: D=$D (engine tree $(git -C $WT rev-parse $D:engine))"

# 1. build
if ! done_ build_D; then
  wait_window; no_cargo
  s=$(date +%s)
  ( cd $WT/engine && $G cargo build --release --locked && $G cargo build --release --locked --example legality_scan &&
    $G cargo build --release --locked --example goldfish && echo "BUILD OK in $(( $(date +%s) - s )) s" ) > $R/build_D.log 2>&1
  if grep -q 'BUILD OK' $R/build_D.log; then
    mkdir -p $W/programs/D
    cp $TGT/release/deckgym $TGT/release/examples/legality_scan $TGT/release/examples/goldfish $W/programs/D/
    ( cd $W/programs/D && sha256sum deckgym legality_scan goldfish > SHA256SUMS )
    echo "$D" > $W/programs/D/SOURCE_COMMIT
    log "build_D OK: $(tail -n 1 $R/build_D.log); $(cut -c1-16 $W/programs/D/SHA256SUMS | tr '\n' ' ')"
    mark build_D
  else
    fail build_D "see $R/build_D.log"; grep -E '^(error|warning: unused)' -A14 $R/build_D.log | head -n 120 >> $LOG
    finish "build failed"
  fi
fi

# 2. the generator reproduces the committed generated files
if done_ build_D && ! done_ gen_D; then
  wait_window; no_cargo
  ( cd $WT/engine && $G cargo build --release --locked --bin card_enum_generator ) > $R/gen_D.log 2>&1
  GEN=$TGT/release/card_enum_generator
  ok=1
  for m in ids database; do
    out=$R/gen_$m.rs; ref=src/card_ids.rs; arg=; [ $m = database ] && { ref=src/database.rs; arg=--database; }
    ( cd $WT/engine && $G $GEN $arg > $out 2>>$R/gen_D.log ) || { ok=0; log "gen_D: the generator failed ($m)"; continue; }
    # no rustfmt on this laptop: the committed files went through cargo fmt, so compare with all whitespace removed
    if cmp -s <(tr -d ' \t\r\n' < $out) <(tr -d ' \t\r\n' < $WT/engine/$ref); then
      log "gen_D: $ref reproduced (whitespace aside; $(diff <(tr -d '\r' < $WT/engine/$ref) <(tr -d '\r' < $out) | grep -c '^[<>]') lines differ in layout only)"
    else
      ok=0; log "gen_D: $ref DIFFERS from the generator's output"; diff -w <(tr -d '\r' < $WT/engine/$ref) <(tr -d '\r' < $out) | head -n 20 >> $LOG; fi
  done
  [ $ok = 1 ] && mark gen_D || fail gen_D "generated files differ"
fi

# 3. the suite
if done_ build_D && ! done_ suite_D; then
  wait_window; no_cargo
  log "suite_D: cargo test --release --features test-utils --locked --no-fail-fast (RUST_TEST_THREADS 2)"
  s=$(date +%s)
  ( cd $WT/engine && RUST_TEST_THREADS=2 $G cargo test --release --features test-utils --locked --no-fail-fast ) > $R/suite_D.log 2>&1
  rc=$?
  res=$(python3 -I - $R/suite_D.log <<'EOF'
import re, sys
t = open(sys.argv[1], errors='replace').read()
p = sum(int(x) for x in re.findall(r'test result: \w+\. (\d+) passed', t))
f = sum(int(x) for x in re.findall(r'(\d+) failed', ' '.join(re.findall(r'test result: [^\n]*', t))))
ig = sum(int(x) for x in re.findall(r'(\d+) ignored', ' '.join(re.findall(r'test result: [^\n]*', t))))
fails = sorted(set(re.findall(r'^---- (\S+)', t, re.M)))
errs = len(re.findall(r'^error(\[E\d+\])?:', t, re.M))
print(f"passed {p} failed {f} ignored {ig} compile_errors {errs} failing {fails[:40]}")
EOF
)
  log "suite_D rc=$rc in $(( $(date +%s) - s )) s: $res"
  case "$res" in *"failed 0 "*"compile_errors 0"*) [ $rc = 0 ] && mark suite_D || fail suite_D "rc=$rc: $res";; *) fail suite_D "$res";; esac
  done_ suite_D || { grep -E '^(error|---- )' -A10 $R/suite_D.log | head -n 120 >> $LOG; finish "suite failed"; }
fi

# 4. side f for the A5 tables it lacks; 5. side d on everything
if done_ suite_D; then
  mkdir -p $W/D
  if [ ! -e $W/D/.from_$D ]; then
    rm -rf $W/D && mkdir -p $W/D
    git -C $WT -c core.autocrlf=false archive $D engine decks | tar -x -C $W/D
    touch $W/D/.from_$D
  fi
  for n in $REF_F; do
    wait_window
    grep -q "^f	$n	" $W/games/summary.tsv 2>/dev/null && continue
    log "replay f $n"
    SCAN_THREADS=8 python3 -u $S/replay3.py f $n >> $R/replays.log 2>&1 || log "replay f $n: exit $?"
  done
  mark ref_F
  for n in $REPLAYS; do
    wait_window
    grep -q "^d	$n	" $W/games/summary.tsv 2>/dev/null && continue
    log "replay d $n"
    SCAN_THREADS=8 python3 -u $S/replay3.py d $n >> $R/replays.log 2>&1 || log "replay d $n: exit $?"
  done
  grep -P '^d\t' $W/games/summary.tsv | cut -c1-300 >> $LOG
  mark replays_D
fi
finish "done"
