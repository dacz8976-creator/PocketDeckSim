#!/bin/bash
# night_r8.sh LANE_COMMIT: the R8 Lane N/I night driver (coordinator-147 §4, coordinator-148). Start it from the laptop session:
#   setsid nohup bash /home/dacz8976/r6v_scratch/rl/results/r8_catchup_2026-10-29/lane/night_r8.sh <LANE_COMMIT> > /dev/null 2>&1 &
# LANE_COMMIT = the commit that adds this folder (LANE_N_PREDICTION.md says so). Everything goes to
# /home/dacz8976/pincand_work/RR_R8_<first 8 of LANE_COMMIT>/ (night/ = this log, the step markers, STOP, SUMMARY.txt).
# Steps, in order, each logged with UTC times; a marker night/<step>.done per finished step (a restart resumes after the last
# one); /home/dacz8976/credit_work/PAUSE is checked between steps (and by the lane and the smoke, between replays and games):
# while it exists, wait. Hard pause for Dustin: kill -STOP -- -$(cat .../RR_R8_<c>/pgids/night_r8.pgid); resume with -CONT.
#    1 preflight   2 worktree (git worktree add --detach /home/dacz8976/lane_r8_w LANE_COMMIT)   3 lane (lane_r8.sh)
#    4 verify (replay_r8.py verify: the S-compare and the prediction check)   5 strength_L (rl/strength/build.sh LANE_COMMIT)
#    6 sc_km3 (+ the harness source hash)   7 k8 (mk_k8.sh + build.sh K8)   8 smoke_b_km3   9 smoke_a_km3   10 smoke_a_kx3
#   11 digest_hunks (digest_hunks.sh)   12 summary
# C: >= 15 GiB free (df /mnt/c) is checked before every cargo step: preflight, the lane (and its suite), strength_L, K8.
# Below it: a STOP (for K8: the kx3 smoke stops only).
# STOP rules (147 §4, 148, LANE_N_PREDICTION.md "Anything else is a STOP"): a failed step writes night/STOP and the driver runs
# only digest_hunks and summary (git and text only), then ends; a restart refuses while night/STOP exists. The kx3-only stops
# (a players/mod.rs merge conflict, a K8 build failure, a kx3 decision over 120 s) write night/KX3_STOPPED and the rest goes on.
# Never: cargo outside the lane / build.sh steps, a push, main or R8's branch moved, ~/pincand's working tree touched, the
# worktree removed (the laptop removes it later with `git worktree remove`), caches dropped.
set -u
PINC=/home/dacz8976/pincand
SCR=/home/dacz8976/r6v_scratch
LW=/home/dacz8976/lane_r8_w
TGT=/home/dacz8976/lane_r8_target
W=/home/dacz8976/pincand_work
PAUSE=/home/dacz8976/credit_work/PAUSE
LD=rl/results/r8_catchup_2026-10-29/lane
HARN=c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149
SC_KM3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1'
X=(':(exclude,icase)*judge*' ':(exclude,icase)*frozen*' ':(exclude,icase)*transcript*' ':(exclude,icase)*run3*' ':(exclude,icase)*weekly_review*' ':(exclude,icase)*battle_log_packets*' ':(exclude,icase)*answers*' ':(exclude,icase)*exam[!p]*' ':(exclude,icase)*exam')
L=$(git -C $SCR rev-parse -q --verify "${1:?usage: night_r8.sh LANE_COMMIT}^{commit}") || { echo "night_r8: no commit $1"; exit 2; }
OUT=$W/RR_R8_${L:0:8}; N=$OUT/night; LOG=$N/night.log
mkdir -p $N $OUT/pgids
echo "$(ps -o pgid= $$ | tr -d ' ')" > $OUT/pgids/night_r8.pgid
log() { echo "$(date -u +%FT%TZ) $*" >> $LOG; }
done_() { [ -e "$N/$1.done" ]; }
mark() { date -u +%FT%TZ > "$N/$1.done"; rm -f "$N/$1.FAILED"; log "step $1 done"; }
STOPPED=0
stop() { echo "$(date -u +%FT%TZ) $1: $2" >> $N/STOP; echo "$(date -u +%FT%TZ) $2" > $N/$1.FAILED; log "STOP at $1: $2"; STOPPED=1; }
kx3_stop() { echo "$(date -u +%FT%TZ) $1: $2" >> $N/KX3_STOPPED; log "KX3 STOP at $1 (the kx3 smoke stops, the rest of Lane N goes on): $2"; }
wait_pause() { local said=0; while [ -e $PAUSE ]; do [ $said = 1 ] || log "paused: $PAUSE exists"; said=1; sleep 60; done; [ $said = 0 ] || log "resumed"; }
begin() { wait_pause; log "step $1 start"; }
free_gib() { echo $(( $(df -B1 --output=avail /mnt/c | tail -n 1 | tr -dc 0-9) / 1073741824 )); }
no_cargo() { while pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null; do log "waiting: another cargo/rustc is running"; sleep 120; done; }
export TMPDIR=$OUT/tmp; mkdir -p $TMPDIR
for v in $(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_|TEST_CARD_SUPPORT_MISSING_ATTACK$)'); do unset "$v"; done
SCRUB=$(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)' | sed 's/^/-u /' | tr '\n' ' ')
log "night_r8 armed (pgid $(cat $OUT/pgids/night_r8.pgid)); lane commit $L; out $OUT"
[ -e $N/STOP ] && { log "night/STOP exists (a STOP was hit before): the laptop must look; remove night/STOP only on the coordinator's word"; exit 0; }
T0=$(date +%s)

# 1. preflight (git and disk only)
if ! done_ preflight; then
  begin preflight
  why=
  [ "$(git -C $SCR show $L:$LD/night_r8.sh | sha256sum | cut -c1-64)" = "$(sha256sum "$0" | cut -c1-64)" ] || why="$why this-driver-is-not-the-lane-commit's"
  d=$(git -C $SCR diff --name-only 63657e0a $L -- engine decks | tr '\n' ' ')
  [ "$d" = "engine/UPSTREAM.md " ] || why="$why engine/decks-v-63657e0a:[$d]"
  d=$(git -C $SCR diff --name-only cdadc04f $L | grep -v "^rl/results/r8_catchup_2026-10-29/" | tr '\n' ' ')
  [ -z "$d" ] || why="$why outside-the-R8-folder-since-cdadc04f:[$d]"
  d=$(git -C $SCR diff --name-only affe56e8 $L -- engine/examples/legality_scan.rs decks | tr '\n' ' ')
  [ -z "$d" ] || why="$why legality_scan/decks-v-affe56e8:[$d]"
  d=$(git -C $SCR diff --name-only b78c8997 $L -- decks rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv rl/results/engine_switch_rules_2026-10/pairs_8.tsv \
        rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv rl/results/engine_switch_rules2_2026-10 rl/results/engine_switch_2026-09-30/screen_with.py "${X[@]}" | tr '\n' ' ')
  [ -z "$d" ] || why="$why R6-replay-inputs-v-b78c8997:[$d]"
  g=$(free_gib); log "C: free $g GiB"; [ "$g" -ge 15 ] || why="$why C:-below-15-GiB($g)"
  log "~/pincand HEAD $(git -C $PINC rev-parse HEAD) ($(git -C $PINC rev-parse --abbrev-ref HEAD)); its tracked changes: $(git -C $PINC status --porcelain --untracked-files=no | wc -l)"
  log "git worktree list:"; git -C $PINC worktree list >> $LOG
  [ -e $TGT ] && log "note: $TGT exists already (a resumed or earlier lane)"
  no_cargo
  if [ -n "$why" ]; then stop preflight "$why"; else mark preflight; fi
fi

# 2. the worktree
if [ $STOPPED = 0 ] && ! done_ worktree; then
  begin worktree
  [ -e $LW ] || git -C $PINC worktree add --detach $LW $L >> $LOG 2>&1
  if [ "$(git -C $LW rev-parse HEAD 2>/dev/null)" = "$L" ] && [ -z "$(git -C $LW status --porcelain)" ]; then mark worktree
  else stop worktree "$LW is not a clean worktree at $L"; fi
fi

# 3. the lane (build, gencmp, card_status, suite, goldfish steps, the 18 replays)
if [ $STOPPED = 0 ] && ! done_ lane; then
  begin lane; no_cargo
  g=$(free_gib); log "C: free $g GiB"
  if [ "$g" -lt 15 ]; then stop lane "C: below 15 GiB ($g)"
  else
    mkdir -p $OUT/prep; echo $L > $OUT/prep/R_COMMIT
    bash $LW/$LD/lane_r8.sh $OUT >> $N/lane_stdout.log 2>&1
    why=; for s in build_R gen_R status_R suite_R goldfish_R replays_R; do [ -e $OUT/prep/$s.done ] || why="$why $s-not-done"; [ -e $OUT/prep/$s.FAILED ] && why="$why $s-FAILED"; done
    log "lane: $(tail -n 1 $OUT/prep/lane_r.log)"
    if [ -z "$why" ]; then mark lane; else stop lane "$why (see $OUT/prep/lane_r.log)"; fi
  fi
fi

# 4. verify: the S-compare and the prediction check
if [ $STOPPED = 0 ] && ! done_ verify; then
  begin verify
  v=$(LANE_OUT=$OUT LANE_WT=$LW python3 -I $LW/$LD/replay_r8.py verify 2>&1 | tail -n 1); log "verify: $v"
  case "$v" in "VERIFY PASS") mark verify;; *) stop verify "$v";; esac
fi

# build_strength NAME REF: rl/strength/build.sh REF -> OUT/strength/NAME/strength, its own build and target folders; checks the record
build_strength() {
  local nm=$1 ref=$2 p=$OUT/strength/$1/strength s rc
  mkdir -p $OUT/strength/$nm
  s=$(date +%s)
  ( cd $LW && env HOME=/home/dacz8976 CARGO_HOME=/home/dacz8976/.cargo STRENGTH_REPO=$PINC STRENGTH_BUILD_DIR=$OUT/strength/${nm}_build \
      STRENGTH_TARGET_DIR=$TGT/strength_$nm STRENGTH_JOBS=2 ionice -c3 bash rl/strength/build.sh $ref $p ) > $OUT/strength/$nm/build.log 2>&1
  rc=$?
  [ $rc = 0 ] && [ -x $p ] || { echo "build.sh rc=$rc (see $OUT/strength/$nm/build.log)"; return 1; }
  local cl; cl=$(grep -m1 -E '^\s*Compiling deckgym v' $OUT/strength/${nm}_build/cargo.log | sed 's/^ *//')
  [ -n "$cl" ] || { echo "binary guard: no 'Compiling deckgym' line in $OUT/strength/${nm}_build/cargo.log"; return 1; }
  python3 -I - $p $(git -C $SCR rev-parse $ref^{commit}) $(git -C $SCR rev-parse $ref:engine) $HARN "$cl" $(( $(date +%s) - s )) <<'EOF'
import hashlib, json, sys
p, k, t, h, cl, secs = sys.argv[1:]
r = json.load(open(p + '.build.json'))
want = dict(engine_ref=k, engine_tree_archived=t, harness_source_sha256=h, jobs='2')
bad = {x: (r.get(x), v) for x, v in want.items() if r.get(x) != v}
sha = hashlib.sha256(open(p, 'rb').read()).hexdigest()
if sha != r.get('program_sha256'):
    bad['program_sha256'] = (r.get('program_sha256'), sha)
print(('RECORD OK ' if not bad else 'RECORD BAD %r ' % bad) + f'program {sha} engine tree {t[:12]} harness {r.get("harness_source_sha256", "")[:12]}; {cl}; {secs} s')
EOF
}

# 5. strength on the lane commit (km3's build for sc_km3 and the km3 smoke)
if [ $STOPPED = 0 ] && ! done_ strength_L; then
  begin strength_L; no_cargo
  g=$(free_gib); log "strength_L: C: free $g GiB"
  if [ "$g" -lt 15 ]; then stop strength_L "C: below 15 GiB ($g)"
  else
    r=$(build_strength L $L); log "strength_L: $r"
    case "$r" in "RECORD OK "*) mark strength_L;;
      *"harness_source_sha256"*) stop strength_L "harness source hash moved from c4f7da21; files that moved it: $(git -C $SCR diff --name-only affe56e8 $L -- rl/strength/src rl/strength/Cargo.toml | tr '\n' ' '); $r";;
      *) stop strength_L "$r";; esac
  fi
fi

# 6. sc_km3 on the lane build, and the harness hash (a)
if [ $STOPPED = 0 ] && ! done_ sc_km3; then
  begin sc_km3
  line=$(cd $LW && env $SCRUB nice -n 19 $OUT/strength/L/strength selfcheck --root $LW --pilot km3 --deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12 2>$N/sc_km3.err | tail -n 1)
  echo "$line" > $N/sc_km3.out; log "sc_km3: $line"
  hs=$(cd $LW && cat rl/strength/src/*.rs rl/strength/Cargo.toml | sha256sum | cut -c1-64); log "harness source hash at the lane commit: $hs"
  if [ "$line" != "$SC_KM3" ]; then stop sc_km3 "digest differs from 81b572198c04d5d1: $line"
  elif [ "$hs" != $HARN ]; then stop sc_km3 "harness source hash $hs, not c4f7da21; files: $(git -C $SCR diff --name-only affe56e8 $L -- rl/strength/src rl/strength/Cargo.toml | tr '\n' ' ')"
  else mark sc_km3; fi
fi

# 7. K8 = kx3 on R8 (a local branch) and its build; a conflict or a build failure stops the kx3 smoke only
if [ $STOPPED = 0 ] && ! done_ k8; then
  begin k8; no_cargo; mkdir -p $OUT/k8
  bash $LW/$LD/mk_k8.sh $L $OUT/k8 > $OUT/k8/mk_k8.log 2>&1; krc=$?
  log "mk_k8 rc=$krc: $(tail -n 1 $OUT/k8/mk_k8.log)"
  if [ $krc = 0 ]; then
    g=$(free_gib); log "strength_K8: C: free $g GiB"
    if [ "$g" -lt 15 ]; then kx3_stop k8 "C: below 15 GiB ($g): K8 not built"
    else
      K8=$(cat $OUT/k8/K8_COMMIT); r=$(build_strength K8 $K8); log "strength_K8: $r"
      case "$r" in "RECORD OK "*) ;; *) kx3_stop k8 "K8 build: $r";; esac
    fi
  elif [ $krc = 3 ]; then kx3_stop k8 "players/mod.rs conflicts (see $OUT/k8/mod_rs.conflict.txt)"
  else kx3_stop k8 "mk_k8.sh exit $krc (see $OUT/k8/mk_k8.log)"; fi
  mark k8
fi

# 8-10. the smoke
smoke() {   # smoke STEP PLAN PROGRAM
  begin $1
  bash $LW/$LD/smoke/smoke_r8.sh $2 $3 $OUT >> $N/smoke_stdout.log 2>&1; local rc=$?
  log "$1: rc=$rc: $(tail -n 1 $OUT/smoke/$2/SUMMARY.txt 2>/dev/null || tail -n 1 $N/smoke_stdout.log)"
  case $rc in 0) mark $1;; 3) kx3_stop $1 "$(tail -n 1 $OUT/smoke/$2/SUMMARY.txt)"; mark $1;; *) stop $1 "rc=$rc: $(tail -n 1 $OUT/smoke/$2/SUMMARY.txt 2>/dev/null)";; esac
}
[ $STOPPED = 0 ] && ! done_ smoke_b_km3 && smoke smoke_b_km3 b_km3 $OUT/strength/L/strength
[ $STOPPED = 0 ] && ! done_ smoke_a_km3 && smoke smoke_a_km3 a_km3 $OUT/strength/L/strength
if [ $STOPPED = 0 ] && ! done_ smoke_a_kx3; then
  if [ -e $N/KX3_STOPPED ]; then log "smoke_a_kx3 skipped: $(tail -n 1 $N/KX3_STOPPED)"; mark smoke_a_kx3
  else smoke smoke_a_kx3 a_kx3 $OUT/strength/K8/strength; fi
fi

# 11. the digest hunks (git only; also after a STOP)
if ! done_ digest_hunks; then
  begin digest_hunks
  bash $LW/$LD/digest_hunks.sh $L > $N/DIGEST_HUNKS.txt 2>&1 && mark digest_hunks || log "digest_hunks failed (see $N/DIGEST_HUNKS.txt)"
  log "digest_hunks: $(tail -n 1 $N/DIGEST_HUNKS.txt)"
fi

# 12. the summary (also after a STOP)
{
  echo "R8 Lane N/I night, lane commit $L, $(date -u +%FT%TZ); this sitting's wall time $(( ($(date +%s) - T0) / 60 )) min"
  echo "markers: $(cd $N && ls *.done 2>/dev/null | tr '\n' ' ')"
  [ -e $N/STOP ] && { echo "STOP:"; cat $N/STOP; }
  [ -e $N/KX3_STOPPED ] && { echo "KX3 STOPPED:"; cat $N/KX3_STOPPED; }
  echo "--- lane log (build, gencmp, card_status, suite, goldfish, replay rows)"; cat $OUT/prep/lane_r.log 2>/dev/null | cut -c1-400
  echo "--- programs"; cat $OUT/programs/SHA256SUMS 2>/dev/null
  echo "--- verify"; cat $OUT/verify/VERIFY.txt 2>/dev/null
  echo "--- strength builds"; grep -h -E '^(engine|program sha256|harness source)' $OUT/strength/*/build.log 2>/dev/null
  echo "--- sc_km3"; cat $N/sc_km3.out 2>/dev/null
  echo "--- K8"; cat $OUT/k8/K8_RECORD.txt 2>/dev/null; tail -n 3 $OUT/k8/mk_k8.log 2>/dev/null
  for p in b_km3 a_km3 a_kx3; do echo "--- smoke $p"; cat $OUT/smoke/$p/SUMMARY.txt 2>/dev/null; done
  echo "--- digest hunks: $(tail -n 1 $N/DIGEST_HUNKS.txt 2>/dev/null) (list in $N/DIGEST_HUNKS.txt)"
  echo "--- night log"; cat $LOG
} > $N/SUMMARY.txt 2>&1
rm -rf $TMPDIR
log "night_r8 end: $([ -e $N/STOP ] && echo STOP || echo done)"
echo "$(date -u +%FT%TZ) $([ -e $N/STOP ] && echo STOP || echo done)" > $N/night.end
rm -f $OUT/pgids/night_r8.pgid
exit 0
