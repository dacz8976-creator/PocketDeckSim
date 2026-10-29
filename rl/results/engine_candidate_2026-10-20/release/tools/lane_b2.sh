#!/bin/bash
# Release follow-through, night lane B v2 (replaces lane_b.sh): the FINAL candidate (PLAN addendum, items 8-10). Night window
# only (02:00-12:50Z; the keeper freezes this process group at 12:55Z). CARGO_BUILD_JOBS 2, STRENGTH_JOBS 2, nice 19, ionice -c3,
# one cargo at a time.
#   1. build_F: one git archive of $R/F_COMMIT (engine + decks) into a fresh folder, release build of the three programs.
#   2. suite_F: the whole suite there (after copying the programs out: cargo test overwrites target/release).
#   3. K_F + strength_r3: kx3 merged onto F_COMMIT (mk_kf.sh), rl/strength/build.sh -> /home/dacz8976/kx_r3/strength.
#   4. sc_km3 (seconds), sc_kx3 in the background: both must equal the pin texts.
#   5. floorF: after lane A ends, the 12 floor re-check pieces on F's deckgym, each also compared with lane A's page.
#   6. replays_F: a sample of the Oct 20 pass's recorded runs on F, each compared with the reference and the Oct 20 build's.
set -u
S=/home/dacz8976/pincand_work/hb
W=/home/dacz8976/pincand_work
REPO=/home/dacz8976/pincand
R=$W/release
F_DIR=$W/F
P=/home/dacz8976/kx_r3/strength
HARN=bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e
SC_KM3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1'
SC_KX3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa'
REPLAYS="08a9b3a_10_cli_k3 08a9b3a_10_cli_kp3 08a9b3a_10_cli_kog3 08a9b3a_10_cli_kta3 08a9b3a_10_cli_km3 08a9b3a_10_goldfish 08a9b3a_10_run_screen 08a9b3a_8b_cloud_new_k3 08a9b3a_8b_cloud_new_km3 08a9b3a_dev_km3_new17 08a9b3a_table_k3 08a9b3a_dev_km3_table 08a9b3a_8_new_km3 08a9b3a_new17_k3 08a9b3a_cov_b2e_km3"
LOG=$R/lane_b.log
mkdir -p $R $W/pgids
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/lane_b.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
done_() { [ -e "$R/$1.done" ]; }
mark() { date -u +%FT%TZ > "$R/$1.done"; rm -f "$R/$1.FAILED"; }
fail() { echo "$(date -u +%FT%TZ) $2" > "$R/$1.FAILED"; log "$1 FAILED: $2"; }
in_window() { local m=$((10#$(date -u +%H) * 60 + 10#$(date -u +%M))); [ $m -ge 120 ] && [ $m -lt 770 ]; }
wait_window() { while ! in_window; do sleep 60; done; }
no_cargo() { while pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null; do log "waiting: another cargo/rustc is running"; sleep 120; done; }
export CARGO_BUILD_JOBS=2
G="nice -n 19 ionice -c3"
SCRUB=$(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)' | sed 's/^/-u /' | tr '\n' ' ')
log "lane_b v2 armed (pgid $(cat $W/pgids/lane_b.pgid))"
wait_window
[ -s $R/F_COMMIT ] || { fail lane_b "no $R/F_COMMIT"; date -u +%FT%TZ > $R/lane_b.end; exit 1; }
F=$(git -C $REPO rev-parse "$(cat $R/F_COMMIT)^{commit}") || { fail lane_b "bad F_COMMIT"; date -u +%FT%TZ > $R/lane_b.end; exit 1; }
log "lane_b v2 start: F=$F (engine tree $(git -C $REPO rev-parse $F:engine))"

# 1. build F
if ! done_ build_F; then
  wait_window; no_cargo
  rm -rf $F_DIR && mkdir -p $F_DIR
  git -C $REPO -c core.autocrlf=false archive $F engine decks | tar -x -C $F_DIR
  find $F_DIR -type f -exec touch {} +
  s=$(date +%s)
  ( cd $F_DIR/engine && unset CARGO_TARGET_DIR &&
    $G cargo build --release --locked && $G cargo build --release --locked --example legality_scan &&
    $G cargo build --release --locked --example goldfish && echo "BUILD OK in $(( $(date +%s) - s )) s" ) > $R/build_F.log 2>&1
  if grep -q 'BUILD OK' $R/build_F.log; then
    mkdir -p $W/programs/F
    cp $F_DIR/engine/target/release/deckgym $F_DIR/engine/target/release/examples/legality_scan $F_DIR/engine/target/release/examples/goldfish $W/programs/F/
    ( cd $W/programs/F && sha256sum deckgym legality_scan goldfish > SHA256SUMS )
    echo "$F" > $W/programs/F/SOURCE_COMMIT
    log "build_F OK: $(tail -n 1 $R/build_F.log); $(cut -c1-16 $W/programs/F/SHA256SUMS | tr '\n' ' ')"
    mark build_F
  else
    fail build_F "see $R/build_F.log"; grep -E '^(error|warning)' -A12 $R/build_F.log | head -n 60 >> $LOG
    date -u +%FT%TZ > $R/lane_b.end; exit 1
  fi
fi

# 2. the suite
if done_ build_F && ! done_ suite_F; then
  wait_window; no_cargo
  log "suite_F: cargo test --release --features test-utils --locked --no-fail-fast (RUST_TEST_THREADS 2)"
  s=$(date +%s)
  ( cd $F_DIR/engine && unset CARGO_TARGET_DIR && RUST_TEST_THREADS=2 $G cargo test --release --features test-utils --locked --no-fail-fast ) > $R/suite_F.log 2>&1
  rc=$?
  res=$(python3 - $R/suite_F.log <<'EOF'
import re, sys
t = open(sys.argv[1], errors='replace').read()
p = sum(int(x) for x in re.findall(r'test result: \w+\. (\d+) passed', t))
f = sum(int(x) for x in re.findall(r'(\d+) failed', ' '.join(re.findall(r'test result: [^\n]*', t))))
fails = sorted(set(re.findall(r'^---- (\S+)', t, re.M)))
errs = len(re.findall(r'^error(\[E\d+\])?:', t, re.M))
print(f"passed {p} failed {f} compile_errors {errs} failing {fails[:40]}")
EOF
)
  log "suite_F rc=$rc in $(( $(date +%s) - s )) s: $res"
  case "$res" in *"failed 0 compile_errors 0"*) [ $rc = 0 ] && mark suite_F || fail suite_F "rc=$rc: $res";; *) fail suite_F "$res";; esac
fi

# 3. K_F and the strength program
if done_ build_F && ! done_ strength_r3; then
  wait_window; no_cargo
  out=$(bash $S/mk_kf.sh $F 2>&1); echo "$out" >> $LOG
  K=$(echo "$out" | sed -n 's/^K=//p' | tail -n 1)
  if [ -z "$K" ]; then fail strength_r3 "mk_kf.sh failed"; else
    echo "$K" > $R/K_F
    T=$(git -C $REPO rev-parse $K:engine)
    if [ -e $P ]; then mv $P $P.old.$(date -u +%H%M%S); mv $P.build.json $P.build.json.old.$(date -u +%H%M%S) 2>/dev/null; fi
    mkdir -p $(dirname $P)
    log "strength_r3: build.sh $K -> $P (STRENGTH_JOBS=2, /home/dacz8976/kx_r3_build)"
    s=$(date +%s)
    ( cd $REPO && env HOME=/home/dacz8976 CARGO_HOME=/home/dacz8976/.cargo STRENGTH_REPO=$REPO \
        STRENGTH_BUILD_DIR=/home/dacz8976/kx_r3_build STRENGTH_TARGET_DIR=/home/dacz8976/kx_r3_build/target STRENGTH_JOBS=2 \
        ionice -c3 bash rl/strength/build.sh $K $P ) > $R/strength_r3.log 2>&1
    rc=$?
    if [ $rc = 0 ] && [ -x $P ]; then
      chk=$(python3 -I - $P $K $T $HARN <<'EOF'
import hashlib, json, sys
p, k, t, h = sys.argv[1:]
r = json.load(open(p + '.build.json'))
want = dict(engine_ref=k, engine_tree_archived=t, harness_source_sha256=h, jobs='2')
bad = {x: (r.get(x), v) for x, v in want.items() if r.get(x) != v}
sha = hashlib.sha256(open(p, 'rb').read()).hexdigest()
if sha != r.get('program_sha256'):
    bad['program_sha256'] = (r.get('program_sha256'), sha)
print(('RECORD OK ' if not bad else 'RECORD BAD %r ' % bad) + sha)
EOF
)
      log "strength_r3 rc=0 in $(( $(date +%s) - s )) s; $chk"
      case "$chk" in "RECORD OK "*) mark strength_r3;; *) fail strength_r3 "$chk";; esac
    else
      fail strength_r3 "build.sh rc=$rc; see $R/strength_r3.log"; tail -n 15 $R/strength_r3.log >> $LOG
    fi
  fi
fi

# 4. the self-checks
if done_ strength_r3 && ! done_ sc_km3; then
  wait_window
  cd $REPO
  line=$(env $SCRUB nice -n 19 $P selfcheck --root $REPO --pilot km3 --deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12 2>$R/sc_km3.err | tail -n 1)
  echo "$line" > $R/sc_km3.out
  log "sc_km3: $line"
  if [ "$line" = "$SC_KM3" ]; then mark sc_km3; else fail sc_km3 "differs from the pin text"; fi
fi
KXPID=
if done_ sc_km3 && ! done_ sc_kx3; then
  wait_window
  log "sc_kx3: started in the background"
  ( cd $REPO; s=$(date +%s)
    env $SCRUB nice -n 19 $P selfcheck --root $REPO --pilot kx3 --deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12 > $R/sc_kx3.full 2>$R/sc_kx3.err
    echo "$? $(( $(date +%s) - s ))" > $R/sc_kx3.rc ) &
  KXPID=$!
fi

# 5. the floor re-check pieces on F, after lane A (one floor run at a time: /tmp is a small tmpfs)
if done_ build_F && ! done_ floorF; then
  while [ ! -e $R/lane_a.end ]; do sleep 60; done
  wait_window
  GSHA_F=$(sha256sum $W/programs/F/deckgym | cut -c1-64)
  log "floorF: floor2.py on F's deckgym ($GSHA_F), each piece also v lane A's page"
  ( cd $REPO && FLOOR2_GYM=$W/programs/F/deckgym FLOOR2_SHA=$GSHA_F FLOOR2_OUT=$W/floor2F FLOOR2_ALSO_VS=$W/floor2 python3 -u $W/floor2.py ) >> $R/floorF.log 2>&1
  log "floorF: exit $?"; cat $W/floor2F/summary.tsv >> $LOG
  mark floorF
fi

# 6. the replay sample on F
if done_ build_F && ! done_ replays_F; then
  for n in $REPLAYS; do
    wait_window
    grep -q "^f	$n	" $W/games/summary.tsv 2>/dev/null && continue
    log "replay f $n"
    python3 -u $S/replay2.py f $n >> $R/replays_F.log 2>&1 || log "replay f $n: exit $?"
  done
  grep '^f	' $W/games/summary.tsv | cut -c1-260 >> $LOG
  mark replays_F
fi

if [ -n "$KXPID" ]; then
  log "waiting for sc_kx3 (pid $KXPID)"
  wait $KXPID
  line=$(tail -n 1 $R/sc_kx3.full); echo "$line" > $R/sc_kx3.out
  log "sc_kx3: rc/secs $(cat $R/sc_kx3.rc): $line"
  if [ "$line" = "$SC_KX3" ]; then mark sc_kx3; else fail sc_kx3 "differs from the pin text"; fi
fi
log "lane_b v2 done"
date -u +%FT%TZ > $R/lane_b.end
