#!/bin/bash
# Dual Fusion release prep (coordinator-035): the night lane for laptop/dual-fusion-release-prep-2026-10-24 (seam + B4b/P-B data + the
# scripted reprint arms). Night window only (or $W/RELEASE_UNTIL); the keeper freezes the group at 12:55Z. CARGO_BUILD_JOBS 2, nice 19.
#   1. build_R   2. gen_R (gencmp: the committed generated files = the generator's output, layout aside)
#   3. status_R  (card_status: no new id MissingTrainer; every B4b Trainer has its base's status)
#   4. suite_R   5. replays_R (side r v side f = main-4d48844, game for game)
set -u
S=/home/dacz8976/pincand_work/hb
W=/home/dacz8976/pincand_work
WT=/home/dacz8976/prep_w
R=$W/prep
TGT=/home/dacz8976/dual_target
REPLAYS="08a9b3a_10_cli_k3 08a9b3a_10_cli_kp3 08a9b3a_10_cli_kog3 08a9b3a_10_cli_kta3 08a9b3a_10_cli_km3 08a9b3a_10_goldfish 08a9b3a_table_k3 08a9b3a_table_kp3 08a9b3a_table_kog3 08a9b3a_dev_km3_table 08a9b3a_dev_kta3_table 08a9b3a_10_run_screen 08a9b3a_new17_k3 08a9b3a_dev_km3_new17 08a9b3a_8b_cloud_new_k3 08a9b3a_8b_cloud_new_km3 08a9b3a_8_new_km3 08a9b3a_cov_b2e_km3"
LOG=$R/lane_r.log
mkdir -p $R $W/pgids
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/lane_r.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
done_() { [ -e "$R/$1.done" ]; }
mark() { date -u +%FT%TZ > "$R/$1.done"; rm -f "$R/$1.FAILED"; }
fail() { echo "$(date -u +%FT%TZ) $2" > "$R/$1.FAILED"; log "$1 FAILED: $2"; }
finish() { log "lane_r end: $1"; date -u +%FT%TZ > $R/lane_r.end; exit 0; }
in_window() { local m=$((10#$(date -u +%H) * 60 + 10#$(date -u +%M))); { [ $m -ge 120 ] && [ $m -lt 770 ]; } || [ "$(date +%s)" -lt "$(cat $W/RELEASE_UNTIL 2>/dev/null || echo 0)" ]; }
wait_window() { while ! in_window; do sleep 60; done; }
no_cargo() { while pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null; do log "waiting: another cargo/rustc is running"; sleep 120; done; }
export CARGO_BUILD_JOBS=2 STRENGTH_JOBS=2 CARGO_TARGET_DIR=$TGT
for v in $(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)'); do unset "$v"; done
G="nice -n 19 ionice -c3"
rm -f $R/lane_r.end
log "lane_r armed (pgid $(cat $W/pgids/lane_r.pgid))"
wait_window
[ -s $R/R_COMMIT ] || { fail lane_r "no R_COMMIT"; finish "no commit"; }
C=$(git -C $WT rev-parse "$(cat $R/R_COMMIT)^{commit}") || { fail lane_r "bad R_COMMIT"; finish "bad commit"; }
[ "$(git -C $WT rev-parse HEAD)" = "$C" ] || { fail lane_r "worktree HEAD is not R_COMMIT"; finish "HEAD moved"; }
[ -z "$(git -C $WT status --porcelain --untracked-files=no)" ] || { fail lane_r "worktree has uncommitted changes"; finish "dirty"; }
log "lane_r start: R=$C"

if ! done_ build_R; then
  wait_window; no_cargo
  s=$(date +%s)
  ( cd $WT/engine && $G cargo build --release --locked && $G cargo build --release --locked --example legality_scan &&
    $G cargo build --release --locked --example goldfish && echo "BUILD OK in $(( $(date +%s) - s )) s" ) > $R/build_R.log 2>&1
  if grep -q 'BUILD OK' $R/build_R.log; then
    mkdir -p $W/programs/R
    cp $TGT/release/deckgym $TGT/release/card_status $TGT/release/card_enum_generator $TGT/release/examples/legality_scan $TGT/release/examples/goldfish $W/programs/R/
    ( cd $W/programs/R && sha256sum deckgym legality_scan goldfish card_status card_enum_generator > SHA256SUMS )
    echo "$C" > $W/programs/R/SOURCE_COMMIT
    log "build_R OK: $(tail -n 1 $R/build_R.log)"; grep -E '^warning' $R/build_R.log | sort | uniq -c >> $LOG
    mark build_R
  else
    fail build_R "see $R/build_R.log"; grep -E '^error' -A14 $R/build_R.log | head -n 120 >> $LOG
    finish "build failed"
  fi
fi

if done_ build_R && ! done_ gen_R; then
  wait_window
  ok=1
  for m in ids database; do
    arg=; ref=src/card_ids.rs; [ $m = database ] && { arg=--database; ref=src/database.rs; }
    ( cd $WT/engine && $G $W/programs/R/card_enum_generator $arg > $R/gen_$m.rs 2>$R/gen_$m.err ) || { ok=0; log "gen_R $m: generator failed"; continue; }
    out=$(python3 -I /home/dacz8976/df0tools/gencmp.py $WT/engine/$ref $R/gen_$m.rs | tail -n 1); log "gen_R $m: $out"
    case "$out" in SAME*) ;; *) ok=0;; esac
  done
  [ $ok = 1 ] && mark gen_R || fail gen_R "generated files differ"
fi

if done_ build_R && ! done_ status_R; then
  wait_window
  ( cd $WT/engine && $G $W/programs/R/card_status --json > $R/card_status.json 2>$R/card_status.err ); log "card_status rc=$?"
  python3 -I - $R/card_status.json $WT/engine/database.json <<'EOF' | tee -a $LOG
import json, sys, collections
cards = json.load(open(sys.argv[1])); cards = cards if isinstance(cards, list) else cards.get('cards', cards)
st = {c['id']: c.get('status') for c in cards}
db = json.load(open(sys.argv[2], encoding='utf-8'))
tr = [(v['id'], v['name'], v.get('effect') or '') for e in db for k, v in e.items() if k == 'Trainer']
by = collections.defaultdict(list)
for i, n, eff in tr: by[(n, eff)].append(i)
new = [i for i in st if i.startswith('B4b ') or i in ('P-B 091', 'P-B 092', 'P-B 093', 'P-B 094', 'P-B 095', 'P-B 096', 'P-B 097', 'P-B 098', 'P-B 099')]
print('card_status: all', len(st), '| new ids by status:', dict(collections.Counter(st[i] for i in new)))
bad = []
for i, n, eff in tr:
    if i.startswith('B4b '):
        bases = [b for b in by[(n, eff)] if not b.startswith('B4b ')]
        if any(st.get(b) != st.get(i) for b in bases):
            bad.append((i, n, st.get(i), [(b, st.get(b)) for b in bases]))
print('B4b Trainers whose status differs from a base printing:', len(bad))
for x in bad[:20]: print('  ', x)
EOF
  mark status_R
fi

if done_ build_R && ! done_ suite_R; then
  wait_window; no_cargo
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

if done_ suite_R; then
  if [ ! -e $W/RR/.from_$C ]; then
    rm -rf $W/RR && mkdir -p $W/RR
    git -C $WT -c core.autocrlf=false archive $C engine decks | tar -x -C $W/RR
    touch $W/RR/.from_$C
  fi
  for n in $REPLAYS; do
    wait_window
    grep -q "^r	$n	" $W/games/summary.tsv 2>/dev/null && continue
    log "replay r $n"
    SCAN_THREADS=8 python3 -u $S/replay3.py r $n >> $R/replays.log 2>&1 || log "replay r $n: exit $?"
  done
  grep -P '^r\t' $W/games/summary.tsv | cut -c1-300 >> $LOG
  mark replays_R
fi
finish "done"
