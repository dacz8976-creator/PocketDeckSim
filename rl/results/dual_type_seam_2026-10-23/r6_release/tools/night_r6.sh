#!/bin/bash
# R6 night 1 (coordinator-072 accepted laptop-058's plan; runbook relplan/r6/RUNBOOK.md). Starts at once (coordinator-073), stops starting
# new work at 12:50Z. nice 19 / ionice -c3, CARGO_BUILD_JOBS 2, the shared target /home/dacz8976/dual_target, C: >= 15 GiB before every cargo step.
# Main does not move tonight. Pause for Dustin: kill -STOP -- -$(cat ~/pincand_work/pgids/night_r6.pgid); resume with -CONT.
#   1. lane on S (lane_s.sh = lane_r.sh v3 with WT=r6s_w): build, gencmp, card_status, suite, the 18 identity replays (side r v f);
#      tonight's ABC lane state is moved aside first (never deleted). Verdict as release_abc.sh's.
#   2. the folded hit-back tests under the default, DECKGYM_FLAT_RETURN_DAMAGE and DECKGYM_ROUND2_OFF (59fc3054's own check), on S.
#   3. strength: rl/strength/build.sh K (e3ddc014: S + kx3's six files) -> /home/dacz8976/kx_r4/strength; the build record checked.
#   4. self-checks km3 (foreground) and kx3 (background): each must equal the pin text; a different digest is a STOP for C.
#   5. the floor pre-use re-check (floor2.py, 12 pieces) on S's deckgym, also v floor2F (main-4d48844's final pages).
#   6. the strength refusal test (STRENGTH_PROGRAM) and the rl/strength Python suite (1 expected failure until the re-pin).
#   7. item 11's branch: the whole suite (separate; it goes to main only on Dustin's word).
set -u
W=/home/dacz8976/pincand_work; HB=$W/hb; N=$W/r6night; REPO=/home/dacz8976/pincand
R=$W/prep; GM=$W/games; TGT=/home/dacz8976/dual_target
SWT=/home/dacz8976/r6s_w; IWT=/home/dacz8976/i11_w
S=affe56e88985e2997a66beb85efaca0c487617bd; K=e3ddc0149bb9d35fda1becbb17ab5f71d9461609; I11=142963eaf7eaa62f742b719ab7b1b99099e21510
P=/home/dacz8976/kx_r4/strength
HARN=c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149
SC_KM3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1'
SC_KX3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa'
LOG=$N/night.log
mkdir -p $N $W/pgids
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/night_r6.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
done_() { [ -e "$N/$1.done" ]; }
mark() { date -u +%FT%TZ > "$N/$1.done"; rm -f "$N/$1.FAILED"; }
fail() { echo "$(date -u +%FT%TZ) $2" > "$N/$1.FAILED"; log "$1 FAILED: $2"; }
end() { log "night_r6 end: $1"; rm -f $W/pgids/night_r6.pgid $W/pgids/lane_r.pgid; rm -rf $TMPDIR; echo "$(date -u +%FT%TZ) $1" > $N/night.end; exit 0; }
# coordinator-073 (Dustin ~00:15Z: "nothing magical about 9 pm and you can start now"): open now, until 12:50Z Oct 29 (1793278200, as
# RELEASE_UNTIL); after that only the usual 02:00-12:50Z window, so no step starts after 12:50Z today
night_ok() { [ "$(date +%s)" -lt 1793278200 ] && return 0; local m=$((10#$(date -u +%H) * 60 + 10#$(date -u +%M))); [ $m -ge 120 ] && [ $m -lt 770 ]; }
wait_night() { while ! night_ok; do sleep 60; done; }
go() { night_ok && return 0; log "skip $1: outside the night window (no new work after 12:50Z)"; return 1; }
no_cargo() { while pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null; do night_ok || break; log "waiting: another cargo/rustc is running"; sleep 120; done
             night_ok || { log "window closed while waiting for cargo/rustc: step skipped"; return 1; }; }
free_gib() { echo $(( $(df -B1 --output=avail /mnt/c | tail -n 1 | tr -dc 0-9) / 1073741824 )); }
disk_ok() { local g=$(free_gib); log "C: free ${g} GiB"; [ "$g" -ge 15 ]; }
suite_res() { python3 -I - "$1" <<'EOF'
import re, sys
t = open(sys.argv[1], errors='replace').read()
p = sum(int(x) for x in re.findall(r'test result: \w+\. (\d+) passed', t))
f = sum(int(x) for x in re.findall(r'(\d+) failed', ' '.join(re.findall(r'test result: [^\n]*', t))))
ig = sum(int(x) for x in re.findall(r'(\d+) ignored', ' '.join(re.findall(r'test result: [^\n]*', t))))
fails = sorted(set(re.findall(r'^---- (\S+)', t, re.M)))
errs = len(re.findall(r'^error(\[E\d+\])?:', t, re.M))
print(f"passed {p} failed {f} ignored {ig} compile_errors {errs} failing {fails[:40]}")
EOF
}
export TMPDIR=/home/dacz8976/relplan/tmp_night; mkdir -p $TMPDIR
export CARGO_BUILD_JOBS=2 STRENGTH_JOBS=2 CARGO_TARGET_DIR=$TGT
for v in $(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)'); do unset "$v"; done
SCRUB=$(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)' | sed 's/^/-u /' | tr '\n' ' ')
G="nice -n 19 ionice -c3"
rm -f $N/night.end
log "night_r6 armed (pgid $(cat $W/pgids/night_r6.pgid)); S=$S K=$K item11=$I11"
wait_night
log "night_r6 start"

# 1. the lane on S
verdict() {
  local why=
  for s in build_R gen_R status_R suite_R replays_R; do [ -e $R/$s.done ] || why="$why $s-not-done"; [ -e $R/$s.FAILED ] && why="$why $s-FAILED"; done
  local n=$(grep -cP '^r\t' $GM/summary.tsv)
  local same=$(grep -P '^r\t' $GM/summary.tsv | awk -F'\t' '$5=="SAME" || ($5=="DIFFERS" && (($2=="08a9b3a_new17_k3" && $6 ~ /^8 differing deals of 8500 /) || ($2=="08a9b3a_dev_km3_new17" && $6 ~ /^7 differing deals of 8500 /) || ($2=="08a9b3a_8_new_km3" && $6 ~ /^1 differing deals of 16000 /)))' | wc -l)
  local vfs=$(grep -P '^r\t' $GM/summary.tsv | grep -cE 'v f: SAME')
  local vf=$(grep -P '^r\t' $GM/summary.tsv | grep -cE 'v f: (DIFFERS|ERROR)')
  local rp=$(grep -P '^r\t' $GM/summary.tsv | grep -c 'rules page: .*: no RULE finding$')
  [ "$n" = 18 ] || why="$why replay-rows-$n"; [ "$same" = 18 ] || why="$why reference-not-as-main-$same"
  [ "$vfs" = 17 ] || why="$why v-f-same-$vfs"; [ "$vf" = 0 ] || why="$why v-f-differs-$vf"
  [ "$rp" = 11 ] || why="$why rules-pages-clean-$rp"
  [ -z "$why" ] && echo PASS || echo "FAIL:$why"
}
if ! done_ lane_S; then
  if [ ! -e $R/ABC_d0792568 ]; then   # tonight's ABC state aside, as release_abc.sh's aside() (never deleted)
    d=$R/ABC_d0792568; mkdir -p $d
    for f in $R/*; do [ -f "$f" ] || continue; mv -n "$f" $d/; done
    cp -p $GM/summary.tsv $GM/summary.tsv.before_aside_ABC_d0792568
    grep -P '^r\t' $GM/summary.tsv > $GM/summary_r_ABC_d0792568.tsv
    grep -vP '^r\t' $GM/summary.tsv > $GM/summary.tsv.new; mv $GM/summary.tsv.new $GM/summary.tsv
    [ -e $GM/r ] && mv $GM/r $GM/r_ABC_d0792568
    [ -e $W/programs/R_ABC_d0792568 ] || cp -a $W/programs/R $W/programs/R_ABC_d0792568
    [ -e $W/RR ] && [ ! -e $W/RR_ABC_d0792568 ] && mv $W/RR $W/RR_ABC_d0792568   # lane_s would rm -rf it (its marker is d0792568's)
    log "aside ABC_d0792568: $(ls $d | wc -l) files; $(wc -l < $GM/summary_r_ABC_d0792568.tsv) r rows; games/r -> r_ABC_d0792568; programs/R copied; RR -> RR_ABC_d0792568"
  fi
  if [ "$(cat $R/R_COMMIT 2>/dev/null)" != $S ]; then   # on a restart, lane_s resumes on S's own markers
    { compgen -G "$R/*.done" || compgen -G "$R/*.FAILED"; } >/dev/null && { log "old markers in $R: stop"; end "old markers"; }
  fi
  [ "$(git -C $SWT rev-parse HEAD)" = $S ] && [ -z "$(git -C $SWT status --porcelain --untracked-files=no)" ] || end "r6s_w is not clean at S"
  disk_ok || end "C: below 15 GiB before the S build"
  echo $S > $R/R_COMMIT
  log "lane_s on S"
  bash $HB/lane_s.sh
  v=$(verdict); log "lane S verdict: $v"
  grep -E '^(card_status: all|   (C1|SP1|P-C) |older|Trainers|STATUS_CHECK)' $R/status_R.txt 2>/dev/null | cut -c1-300 | sed 's/^/  /' | tee -a $LOG
  log "programs/R (S): $(cut -c1-16 $W/programs/R/SHA256SUMS | tr '\n' ' ') source $(cat $W/programs/R/SOURCE_COMMIT)"
  echo "$v" > $N/lane_S.verdict
  [ "$v" = PASS ] && mark lane_S || fail lane_S "$v"
fi
S_BUILT=0; [ -e $R/build_R.done ] && [ -e $R/suite_R.done ] && [ "$(cat $W/programs/R/SOURCE_COMMIT 2>/dev/null)" = $S ] && S_BUILT=1
[ $S_BUILT = 1 ] || log "S not built and tested (build_R/suite_R/SOURCE_COMMIT): steps 2, 3, 4, 5, 6 skipped"

# 2. the folded hit-back tests under the switches
if [ $S_BUILT = 1 ] && ! done_ switch_runs && go switch_runs && no_cargo && disk_ok; then
  ok=1
  for e in "" "DECKGYM_FLAT_RETURN_DAMAGE=1" "DECKGYM_ROUND2_OFF=1"; do
    ( cd $SWT/engine && env $e RUST_TEST_THREADS=2 $G cargo test --release --features test-utils --locked --no-fail-fast \
        --test rules_repair_hit_back_attack_damage --test rules_repair_return_damage_weakness ) > $N/switch_${e%%=*}.log 2>&1
    r=$(suite_res $N/switch_${e%%=*}.log); log "switch runs [${e:-default}] files: $r"
    case "$r" in "passed 32 failed 0 "*"compile_errors 0"*) ;; *) ok=0;; esac
  done
  ( cd $SWT/engine && env DECKGYM_ROUND2_OFF=1 RUST_TEST_THREADS=2 $G cargo test --release --features test-utils --locked --no-fail-fast --lib attack_cut_to_zero_and_hit_back_tests ) > $N/switch_core.log 2>&1
  r=$(suite_res $N/switch_core.log); log "switch runs [ROUND2_OFF] core module: $r"
  case "$r" in "passed 14 failed 0 "*"compile_errors 0"*) ;; *) ok=0;; esac
  [ $ok = 1 ] && mark switch_runs || fail switch_runs "see $N/switch_*.log"
fi

# 3. the strength program on K
if [ $S_BUILT = 1 ] && ! done_ strength_K && go strength_K && no_cargo; then
  if disk_ok; then
    [ -e $P ] && { log "$P exists: moved aside"; mv $P $P.old.$(date -u +%H%M%S); mv $P.build.json $P.build.json.old.$(date -u +%H%M%S) 2>/dev/null; }
    mkdir -p $(dirname $P)
    T=$(git -C $REPO rev-parse $K:engine)
    log "strength: build.sh $K -> $P (STRENGTH_JOBS=2, build dir /home/dacz8976/kx_r4_build, target $TGT)"
    s=$(date +%s)
    ( cd $SWT && env HOME=/home/dacz8976 CARGO_HOME=/home/dacz8976/.cargo STRENGTH_REPO=$REPO \
        STRENGTH_BUILD_DIR=/home/dacz8976/kx_r4_build STRENGTH_TARGET_DIR=$TGT STRENGTH_JOBS=2 \
        ionice -c3 bash rl/strength/build.sh $K $P ) > $N/strength_K.log 2>&1
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
      log "strength rc=0 in $(( $(date +%s) - s )) s; $chk"
      case "$chk" in "RECORD OK "*) mark strength_K;; *) fail strength_K "$chk";; esac
    else
      fail strength_K "build.sh rc=$rc; see $N/strength_K.log"; tail -n 25 $N/strength_K.log >> $LOG
    fi
  else
    fail strength_K "C: below 15 GiB"
  fi
fi

# 4. the self-checks
KXPID=
if done_ strength_K && ! done_ sc_km3 && go sc_km3; then
  line=$(cd $SWT && env $SCRUB nice -n 19 $P selfcheck --root $SWT --pilot km3 --deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12 2>$N/sc_km3.err | tail -n 1)
  echo "$line" > $N/sc_km3.out; log "sc_km3: $line"
  if [ "$line" = "$SC_KM3" ]; then mark sc_km3; else fail sc_km3 "STOP: differs from the pin text (coordinator; new texts need Dustin)"; fi
fi
if done_ strength_K && ! done_ sc_kx3 && go sc_kx3; then
  log "sc_kx3: started in the background"
  ( cd $SWT; s=$(date +%s)
    env $SCRUB nice -n 19 $P selfcheck --root $SWT --pilot kx3 --deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12 > $N/sc_kx3.full 2>$N/sc_kx3.err
    echo "$? $(( $(date +%s) - s ))" > $N/sc_kx3.rc ) &
  KXPID=$!
fi

# 5. the floor pre-use re-check on S's deckgym
if [ $S_BUILT = 1 ] && ! done_ floorS && go floorS; then
  GSHA=$(sha256sum $W/programs/R/deckgym | cut -c1-64)
  log "floorS: floor2.py on S's deckgym ($GSHA), each piece also v floor2F"
  ( cd $REPO && FLOOR2_GYM=$W/programs/R/deckgym FLOOR2_SHA=$GSHA FLOOR2_OUT=$W/floor2S FLOOR2_ALSO_VS=$W/floor2F python3 -u $W/floor2.py ) >> $N/floorS.log 2>&1
  frc=$?; log "floorS: exit $frc"; cat $W/floor2S/summary.tsv 2>/dev/null | cut -c1-300 >> $LOG
  # every page must equal main-4d48844's final page: SAME v the recorded page, or DIFFERS from it but SAME v floor2F (brew-07, brew-09)
  fv=$(awk -F'\t' '$4=="SAME" || ($4=="DIFFERS" && $5 ~ /v floor2F: exit 0$/) {k++} END {print NR+0, k+0}' $W/floor2S/summary.tsv 2>/dev/null)
  if [ $frc = 0 ] && [ "$fv" = "12 12" ]; then mark floorS; else fail floorS "exit $frc; pieces/equal-to-main-4d48844: ${fv:-none}"; fi
fi

# 6. the strength refusal test and the rl/strength Python suite
if done_ strength_K && ! done_ strength_tests; then
  ( cd $SWT/rl/strength && env $SCRUB STRENGTH_PROGRAM=$P python3 -B -m unittest -v test_strength_card_support ) > $N/strength_refusal.log 2>&1
  rrc=$?; log "strength refusal test: rc=$rrc $(grep -E '^(Ran|OK|FAILED)' $N/strength_refusal.log | tr '\n' ' ')"
  ( cd $SWT/rl/strength && env $SCRUB python3 -B -m unittest test_slow_report test_slow_report_runloop test_slow_report_process test_slow_report_page test_slow_report_registration test_strength_prereg_use test_strength_report test_slow_report_existing test_slow_report_paired test_split_collect test_strength_card_support ) > $N/strength_py.log 2>&1
  log "rl/strength Python suite: rc=$? $(grep -E '^(Ran|OK|FAILED)' $N/strength_py.log | tr '\n' ' '); failing: $(grep -E '^(FAIL|ERROR):' $N/strength_py.log | cut -c1-160 | tr '\n' ';')"
  # the refusal test must really run its 4 tests (no "OK (skipped=4)"); the Python suite's one expected failure is read by hand
  [ $rrc = 0 ] && grep -q '^Ran 4 tests' $N/strength_refusal.log && grep -qx 'OK' $N/strength_refusal.log && mark strength_tests || fail strength_tests "refusal test rc=$rrc"
fi

# 7. item 11's branch: the whole suite
if ! done_ suite_I11 && go suite_I11 && no_cargo; then
  if [ "$(git -C $IWT rev-parse HEAD)" = $I11 ] && [ -z "$(git -C $IWT status --porcelain --untracked-files=no)" ] && disk_ok; then
    s=$(date +%s)
    ( cd $IWT/engine && RUST_TEST_THREADS=2 $G cargo test --release --features test-utils --locked --no-fail-fast ) > $N/suite_I11.log 2>&1
    rc=$?; r=$(suite_res $N/suite_I11.log)
    log "suite item 11 rc=$rc in $(( $(date +%s) - s )) s: $r"
    case "$r" in *"failed 0 "*"compile_errors 0"*) [ $rc = 0 ] && mark suite_I11 || fail suite_I11 "rc=$rc: $r";; *) fail suite_I11 "$r";; esac
    done_ suite_I11 || grep -E '^(error|---- )' -A10 $N/suite_I11.log | head -n 80 >> $LOG
  else
    fail suite_I11 "i11_w not clean at $I11, or C: below 15 GiB"
  fi
fi

if [ -n "$KXPID" ]; then
  log "waiting for sc_kx3 (pid $KXPID)"; wait $KXPID
  line=$(tail -n 1 $N/sc_kx3.full); echo "$line" > $N/sc_kx3.out
  log "sc_kx3: rc/secs $(cat $N/sc_kx3.rc): $line"
  if [ "$line" = "$SC_KX3" ]; then mark sc_kx3; else fail sc_kx3 "STOP: differs from the pin text (coordinator; new texts need Dustin)"; fi
fi
log "markers: $(cd $N && ls *.done *.FAILED 2>/dev/null | tr '\n' ' ')"
end "done"
