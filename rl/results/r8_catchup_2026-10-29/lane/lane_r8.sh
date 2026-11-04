#!/bin/bash
# lane_r8.sh OUT: Lane N for R8 (coordinator-147 §4, coordinator-148). Run by night_r8.sh; never by hand on a dirty tree.
# PROVENANCE: a copy of R6's lane_s.sh (rl/results/dual_type_seam_2026-10-23/r6_release/tools/lane_s.sh, sha256
# 14d5753fbb2f79966b71e23f6b034130e7d138eaa7a051f6c9b61f8519c6ef5a, = lane_r.sh v3 with WT=r6s_w; TOOLS.txt:7,13), adapted to R8.
# CHANGES from lane_s.sh (everything else, the step order and the logs, is R6's):
#   1. WT=/home/dacz8976/lane_r8_w (a detached worktree of ~/pincand at the lane commit, made by night_r8.sh), not r6s_w.
#   2. Its own CARGO_TARGET_DIR /home/dacz8976/lane_r8_target, not the shared dual_target (coordinator-148 §2.8).
#   3. Outputs under OUT=/home/dacz8976/pincand_work/RR_R8_<short lane commit> (prep/, programs/, RR/, games/), never R6's
#      prep/, programs/R, RR or games/ (lane_s.sh wrote $W/prep, $W/programs/R, $W/RR, $W/games).
#   4. No night window (in_window/wait_window/RELEASE_UNTIL removed): a PAUSE check instead, before every step and every
#      replay: while /home/dacz8976/credit_work/PAUSE exists, wait (minute steps).
#   5. The environment clearing also removes TEST_CARD_SUPPORT_MISSING_ATTACK (the test-only refusal variable).
#   6. The binary guard: before and after each build the sha256 of every binary it should make is recorded, and the build log
#      must hold a "Compiling deckgym" line. No such line, a binary missing, or a hash unchanged where a build was expected:
#      STOP (stale binary suspected). The hashes and the Compiling line go to the log.
#   7. gencmp: the committed copy rl/results/dual_type_seam_2026-10-23/tools/gencmp.py in the worktree (byte-equal to the
#      deleted /home/dacz8976/df0tools/gencmp.py that R6 ran: r6_release/RUN_CONTEXT.txt:15).
#   8. status_R: R6's checks plus the exact counts of the prediction: 4,577 cards = 4,565 Complete + 12 RulesUnverified; the 260
#      new = 256 Complete + 4 RulesUnverified (C1 015, C1 051, C1 135, C1 184), 0 Missing*.
#   9. A goldfish_R step after suite_R (lane_plan §2.3): the plain goldfish rebuilt (guard), `cargo test --release --locked
#      --test goldfish_card_support_test` (1 passed), the test-utils goldfish rebuilt (guard); `strings` counts of
#      TEST_CARD_SUPPORT_MISSING_ATTACK in the plain deckgym and the plain goldfish (expected 0 lines each).
#  10. replays_R: replay_r8.py (this folder) instead of $S/replay3.py; the archive is OUT/RR; the summary OUT/games/summary.tsv.
#  11. The pgid file is OUT/pgids/lane_r8.pgid.
#   1. build_R   2. gen_R   3. status_R   4. suite_R   5. goldfish_R   6. replays_R (side r v the 08a9b3a references, and v R6 S)
set -u
OUT=${1:?usage: lane_r8.sh OUT}
W=/home/dacz8976/pincand_work
WT=/home/dacz8976/lane_r8_w
T=$WT/rl/results/r8_catchup_2026-10-29/lane
R=$OUT/prep
TGT=/home/dacz8976/lane_r8_target
PAUSE=/home/dacz8976/credit_work/PAUSE
REPLAYS="08a9b3a_10_cli_k3 08a9b3a_10_cli_kp3 08a9b3a_10_cli_kog3 08a9b3a_10_cli_kta3 08a9b3a_10_cli_km3 08a9b3a_10_goldfish 08a9b3a_table_k3 08a9b3a_table_kp3 08a9b3a_table_kog3 08a9b3a_dev_km3_table 08a9b3a_dev_kta3_table 08a9b3a_10_run_screen 08a9b3a_new17_k3 08a9b3a_dev_km3_new17 08a9b3a_8b_cloud_new_k3 08a9b3a_8b_cloud_new_km3 08a9b3a_8_new_km3 08a9b3a_cov_b2e_km3"
LOG=$R/lane_r.log
case "$OUT" in $W/RR_R8_*) ;; *) echo "lane_r8.sh: OUT must be $W/RR_R8_<commit>"; exit 2;; esac
mkdir -p $R $OUT/pgids
echo "$(ps -o pgid= $$ | tr -d ' ')" > $OUT/pgids/lane_r8.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
done_() { [ -e "$R/$1.done" ]; }
mark() { date -u +%FT%TZ > "$R/$1.done"; rm -f "$R/$1.FAILED"; }
fail() { echo "$(date -u +%FT%TZ) $2" > "$R/$1.FAILED"; log "$1 FAILED: $2"; }
finish() { log "lane_r8 end: $1"; date -u +%FT%TZ > $R/lane_r.end; exit 0; }
wait_pause() { local said=0; while [ -e $PAUSE ]; do [ $said = 1 ] || log "paused: $PAUSE exists"; said=1; sleep 60; done; [ $said = 0 ] || log "resumed"; }
no_cargo() { while pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null; do log "waiting: another cargo/rustc is running"; sleep 120; done; }
hashes() { local f; for f in "$@"; do if [ -e "$f" ]; then sha256sum "$f" | cut -c1-64; else echo absent; fi; done | tr '\n' ' '; }
# guard LABEL BUILDLOG "PRE-HASHES" FILE...: the binary guard (change 6); prints one line, returns 1 on a STOP
guard() {
  local label=$1 lg=$2 pre=$3 i=1 f a b; shift 3
  local post; post=$(hashes "$@")
  local line; line=$(grep -m1 -E '^\s*Compiling deckgym v' "$lg" | sed 's/^ *//')
  [ -n "$line" ] || { echo "$label: STOP binary guard: no 'Compiling deckgym' line in $lg"; return 1; }
  for f in "$@"; do
    a=$(echo $pre | cut -d' ' -f$i); b=$(echo $post | cut -d' ' -f$i); i=$((i + 1))
    [ "$b" = absent ] && { echo "$label: STOP binary guard: $f missing after the build"; return 1; }
    [ "$a" = "$b" ] && { echo "$label: STOP binary guard: $f unchanged by the build ($b)"; return 1; }
  done
  echo "$label: guard OK ($line); after: $(for f in "$@"; do echo -n "$(basename $f)=$(sha256sum $f | cut -c1-16) "; done)"
}
export CARGO_BUILD_JOBS=2 STRENGTH_JOBS=2 CARGO_TARGET_DIR=$TGT
for v in $(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_|TEST_CARD_SUPPORT_MISSING_ATTACK$)'); do unset "$v"; done
G="nice -n 19 ionice -c3"
rm -f $R/lane_r.end
log "lane_r8 armed (pgid $(cat $OUT/pgids/lane_r8.pgid))"
wait_pause
[ -s $R/R_COMMIT ] || { fail lane_r "no R_COMMIT"; finish "no commit"; }
C=$(git -C $WT rev-parse "$(cat $R/R_COMMIT)^{commit}") || { fail lane_r "bad R_COMMIT"; finish "bad commit"; }
[ "$(git -C $WT rev-parse HEAD)" = "$C" ] || { fail lane_r "worktree HEAD is not R_COMMIT"; finish "HEAD moved"; }
[ -z "$(git -C $WT status --porcelain --untracked-files=no)" ] || { fail lane_r "worktree has uncommitted changes"; finish "dirty"; }
log "lane_r8 start: R=$C"

if ! done_ build_R; then
  wait_pause; no_cargo
  BINS="$TGT/release/deckgym $TGT/release/card_status $TGT/release/card_enum_generator $TGT/release/examples/legality_scan $TGT/release/examples/goldfish"
  pre=$(hashes $BINS); log "build_R: before: $pre"
  s=$(date +%s)
  ( cd $WT/engine && $G cargo build --release --locked && $G cargo build --release --locked --example legality_scan &&
    $G cargo build --release --locked --example goldfish && echo "BUILD OK in $(( $(date +%s) - s )) s" ) > $R/build_R.log 2>&1
  if grep -q 'BUILD OK' $R/build_R.log; then
    g=$(guard build_R $R/build_R.log "$pre" $BINS); log "$g"
    case "$g" in *"guard OK"*) ;; *) fail build_R "$g"; finish "stale binary suspected";; esac
    mkdir -p $OUT/programs
    cp $BINS $OUT/programs/
    ( cd $OUT/programs && sha256sum deckgym legality_scan goldfish card_status card_enum_generator > SHA256SUMS )
    echo "$C" > $OUT/programs/SOURCE_COMMIT
    log "build_R OK: $(tail -n 1 $R/build_R.log)"; grep -E '^warning' $R/build_R.log | sort | uniq -c >> $LOG
    mark build_R
  else
    fail build_R "see $R/build_R.log"; grep -E '^error' -A14 $R/build_R.log | head -n 120 >> $LOG
    finish "build failed"
  fi
fi

if done_ build_R && ! done_ gen_R; then
  wait_pause
  ok=1
  for m in ids database; do
    arg=; ref=src/card_ids.rs; [ $m = database ] && { arg=--database; ref=src/database.rs; }
    ( cd $WT/engine && $G $OUT/programs/card_enum_generator $arg > $R/gen_$m.rs 2>$R/gen_$m.err ) || { ok=0; log "gen_R $m: generator failed"; continue; }
    out=$(python3 -I $WT/rl/results/dual_type_seam_2026-10-23/tools/gencmp.py $WT/engine/$ref $R/gen_$m.rs | tail -n 1); log "gen_R $m: $out"
    case "$out" in SAME*) ;; *) ok=0;; esac
  done
  [ $ok = 1 ] && mark gen_R || fail gen_R "generated files differ"
fi

if done_ build_R && ! done_ status_R; then
  wait_pause
  ( cd $WT/engine && $G $OUT/programs/card_status --json > $R/card_status.json 2>$R/card_status.err ); src=$?; log "card_status rc=$src"
  python3 -I - $R/card_status.json $WT/engine/database.json > $R/status_R.txt 2>&1 <<'EOF'
import json, sys, collections
cards = json.load(open(sys.argv[1])); cards = cards if isinstance(cards, list) else cards.get('cards', cards)
st = {c['id']: c.get('status') for c in cards}
db = json.load(open(sys.argv[2], encoding='utf-8'))
tr = [(v['id'], v['name'], v.get('effect') or '') for e in db for k, v in e.items() if k == 'Trainer']
by = collections.defaultdict(list)
for i, n, eff in tr: by[(n, eff)].append(i)
NEW = ('C1 ', 'SP1 ', 'P-C ')
new = [i for i in st if i.startswith(NEW)]
print('card_status: all', len(st), '| new C1/SP1/P-C:', len(new), dict(sorted(collections.Counter(st[i] for i in new).items())))
for p in NEW:
    sub = [i for i in new if i.startswith(p)]
    print('  ', p.strip(), len(sub), dict(sorted(collections.Counter(st[i] for i in sub).items())))
old_bad = sorted(i for i in st if not i.startswith(NEW) and st[i] not in ('Complete', 'RulesUnverified'))
print('older cards neither Complete nor RulesUnverified:', len(old_bad), old_bad[:20])
bad = [(k, [(i, st.get(i)) for i in ids]) for k, ids in by.items()
       if any(i.startswith(NEW + ('B4b ',)) for i in ids) and len({st.get(i) for i in ids}) > 1]
print('Trainers with a new or B4b printing (same name and text) whose printings differ in status:', len(bad))
for k, x in bad[:20]: print('  ', k[0], x)
print('incomplete new ids:', sorted((i, st[i]) for i in new if st[i] != 'Complete'))
# R8 (change 8): the prediction's exact counts
allc = dict(sorted(collections.Counter(st.values()).items()))
newc = dict(sorted(collections.Counter(st[i] for i in new).items()))
ru_new = sorted(i for i in new if st[i] == 'RulesUnverified')
print('all by status:', allc)
exact = (allc == {'Complete': 4565, 'RulesUnverified': 12} and newc == {'Complete': 256, 'RulesUnverified': 4}
         and ru_new == ['C1 015', 'C1 051', 'C1 135', 'C1 184'])
print('exact R8 counts (4,565 + 12; new 256 + 4: C1 015, C1 051, C1 135, C1 184):', 'yes' if exact else 'NO')
ok = len(st) == 4577 and len(new) == 260 and not old_bad and not bad and exact
print('STATUS_CHECK', 'OK' if ok else 'BAD')
EOF
  grep -v '^incomplete new ids:' $R/status_R.txt | cut -c1-600 >> $LOG
  if [ $src = 0 ] && grep -q '^STATUS_CHECK OK' $R/status_R.txt; then mark status_R; else fail status_R "card_status rc=$src; $(tail -n 1 $R/status_R.txt)"; fi
fi

if done_ build_R && ! done_ suite_R; then
  wait_pause; no_cargo
  s=$(date +%s)
  ( cd $WT/engine && RUST_TEST_THREADS=2 $G cargo test --release --features test-utils --locked --no-fail-fast ) > $R/suite_R.log 2>&1
  rc=$?
  res=$(python3 -I - $R/suite_R.log <<'EOF'
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
  log "suite_R rc=$rc in $(( $(date +%s) - s )) s: $res"
  case "$res" in *"failed 0 "*"compile_errors 0"*) [ $rc = 0 ] && mark suite_R || fail suite_R "rc=$rc: $res";; *) fail suite_R "$res";; esac
  done_ suite_R || { grep -E '^(error|---- )' -A10 $R/suite_R.log | head -n 120 >> $LOG; finish "suite failed"; }
fi

if done_ suite_R && ! done_ goldfish_R; then
  wait_pause; no_cargo
  GF=$TGT/release/examples/goldfish; ok=1
  pre=$(hashes $GF)
  ( cd $WT/engine && $G cargo build --release --locked --example goldfish ) > $R/goldfish_plain.log 2>&1 || ok=0
  if [ "$pre" = "$(hashes $OUT/programs/goldfish)" ]; then
    # the suite left build_R's plain goldfish in place (not replaced by a test-utils one): the same source may give the same
    # bytes, so only the Compiling line is required here; the strings count below shows it is the plain build
    if grep -qE '^\s*Compiling deckgym v' $R/goldfish_plain.log; then g="goldfish_plain: guard OK (the suite left the plain goldfish; Compiling line present; $(hashes $GF | cut -c1-16))"
    else g="goldfish_plain: STOP binary guard: no 'Compiling deckgym' line"; fi
  else g=$(guard goldfish_plain $R/goldfish_plain.log "$pre" $GF); fi
  log "$g"; case "$g" in *"guard OK"*) ;; *) ok=0;; esac
  nstr() { command -v strings >/dev/null || { echo NA; return; }; strings "$1" | grep -c TEST_CARD_SUPPORT_MISSING_ATTACK; }
  n1=$(nstr $OUT/programs/deckgym); n2=$(nstr $OUT/programs/goldfish); n3=$(nstr $GF)
  log "goldfish_R strings TEST_CARD_SUPPORT_MISSING_ATTACK: programs/deckgym $n1, programs/goldfish $n2, rebuilt plain goldfish $n3 (each expected 0)"
  [ "$n1$n2$n3" = 000 ] || ok=0
  ( cd $WT/engine && RUST_TEST_THREADS=2 $G cargo test --release --locked --test goldfish_card_support_test ) > $R/goldfish_test.log 2>&1; grc=$?
  gres=$(grep -E '^test result:' $R/goldfish_test.log | tr '\n' ' '); log "goldfish_R plain test rc=$grc: $gres"
  { [ $grc = 0 ] && echo "$gres" | grep -q 'ok\. 1 passed; 0 failed'; } || ok=0
  pre=$(hashes $GF)
  ( cd $WT/engine && $G cargo build --release --locked --features test-utils --example goldfish ) > $R/goldfish_tu.log 2>&1 || ok=0
  g=$(guard goldfish_test_utils $R/goldfish_tu.log "$pre" $GF); log "$g"; case "$g" in *"guard OK"*) ;; *) ok=0;; esac
  log "goldfish_R test-utils goldfish strings count: $(nstr $GF) (expected 1 or more; report only)"
  [ $ok = 1 ] && mark goldfish_R || { fail goldfish_R "see $R/goldfish_*.log"; finish "goldfish steps failed"; }
fi

if done_ goldfish_R && ! { done_ gen_R && done_ status_R; }; then finish "gen_R or status_R failed: replays skipped"; fi
if done_ goldfish_R; then
  if [ ! -e $OUT/RR/.from_$C ]; then
    [ -e $OUT/RR ] && { fail replays_R "$OUT/RR exists without .from_$C: look before removing"; finish "RR not ours"; }
    mkdir -p $OUT/RR
    git -C $WT -c core.autocrlf=false archive $C engine decks | tar -x -C $OUT/RR
    touch $OUT/RR/.from_$C
  fi
  for n in $REPLAYS; do
    wait_pause
    grep -q "^r	$n	" $OUT/games/summary.tsv 2>/dev/null && continue
    log "replay r $n"
    LANE_OUT=$OUT LANE_WT=$WT SCAN_THREADS=8 python3 -u $T/replay_r8.py r $n >> $R/replays.log 2>&1 || log "replay r $n: exit $?"
  done
  grep -P '^r\t' $OUT/games/summary.tsv | cut -c1-400 >> $LOG
  [ "$(grep -cP '^r\t' $OUT/games/summary.tsv)" = 18 ] && mark replays_R || fail replays_R "not 18 replay rows"
fi
finish "done"
