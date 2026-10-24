#!/bin/bash
# The B4b + P-B 099 data-pin DRY RUN (coordinator GO, Oct 23; not adopted, never merged). Night window only; starts after
# the dual-type lane's replays are done (one cargo at a time). CARGO_BUILD_JOBS 2, nice 19, ionice -c3. It MEASURES:
#   1. build_P: the three programs (+ card_status, card_enum_generator) from the dry-run worktree at P_COMMIT.
#   2. gen_P:   our generator on the new database.json reproduces upstream's generated files (whitespace aside);
#               the incremental attack/ability maps list any unmapped new text (expected: none).
#   3. status_P: card_status --json, the 438 new ids by status (Trainer reprints without an id arm show up here).
#   4. suite_P: the whole suite; failures are recorded, not fixed (expected: the 3879-card pins, Trainer coverage).
#   5. replays_P: side p on the k3 table and the five CLI rows, each compared game for game with side f.
set -u
S=/home/dacz8976/pincand_work/hb
W=/home/dacz8976/pincand_work
WT=/home/dacz8976/datapin_w
R=$W/datapin
TGT=/home/dacz8976/dual_target
REPLAYS="08a9b3a_10_cli_k3 08a9b3a_10_cli_kp3 08a9b3a_10_cli_kog3 08a9b3a_10_cli_kta3 08a9b3a_10_cli_km3 08a9b3a_table_k3"
LOG=$R/lane_p.log
mkdir -p $R $W/pgids
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/lane_p.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
done_() { [ -e "$R/$1.done" ]; }
mark() { date -u +%FT%TZ > "$R/$1.done"; rm -f "$R/$1.FAILED"; }
fail() { echo "$(date -u +%FT%TZ) $2" > "$R/$1.FAILED"; log "$1 FAILED: $2"; }
finish() { log "lane_p end: $1"; date -u +%FT%TZ > $R/lane_p.end; exit 0; }
# the night window, or earlier when Dustin releases the laptop ($W/RELEASE_UNTIL: an epoch second, at most the next 12:50Z)
in_window() { local m=$((10#$(date -u +%H) * 60 + 10#$(date -u +%M))); { [ $m -ge 120 ] && [ $m -lt 770 ]; } || [ "$(date +%s)" -lt "$(cat $W/RELEASE_UNTIL 2>/dev/null || echo 0)" ]; }
wait_window() { while ! in_window; do sleep 60; done; }
no_cargo() { while pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null; do log "waiting: another cargo/rustc is running"; sleep 120; done; }
export CARGO_BUILD_JOBS=2 CARGO_TARGET_DIR=$TGT
for v in $(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)'); do unset "$v"; done
G="nice -n 19 ionice -c3"
rm -f $R/lane_p.end
log "lane_p armed (pgid $(cat $W/pgids/lane_p.pgid)); waiting for $W/dual/replays_D.done"
while [ ! -e $W/dual/replays_D.done ]; do sleep 120; done
wait_window
[ -s $R/P_COMMIT ] || { fail lane_p "no P_COMMIT"; finish "no commit"; }
P=$(git -C $WT rev-parse "$(cat $R/P_COMMIT)^{commit}") || { fail lane_p "bad P_COMMIT"; finish "bad commit"; }
[ "$(git -C $WT rev-parse HEAD)" = "$P" ] || { fail lane_p "worktree HEAD is not P_COMMIT"; finish "HEAD moved"; }
[ -z "$(git -C $WT status --porcelain --untracked-files=no)" ] || { fail lane_p "worktree has uncommitted changes"; finish "dirty"; }
log "lane_p start: P=$P"

if ! done_ build_P; then
  wait_window; no_cargo
  s=$(date +%s)
  ( cd $WT/engine && $G cargo build --release --locked && $G cargo build --release --locked --example legality_scan &&
    $G cargo build --release --locked --example goldfish && echo "BUILD OK in $(( $(date +%s) - s )) s" ) > $R/build_P.log 2>&1
  if grep -q 'BUILD OK' $R/build_P.log; then
    mkdir -p $W/programs/P
    cp $TGT/release/deckgym $TGT/release/card_status $TGT/release/card_enum_generator $TGT/release/examples/legality_scan $TGT/release/examples/goldfish $W/programs/P/
    ( cd $W/programs/P && sha256sum deckgym legality_scan goldfish card_status card_enum_generator > SHA256SUMS )
    echo "$P" > $W/programs/P/SOURCE_COMMIT
    log "build_P OK: $(tail -n 1 $R/build_P.log)"
    mark build_P
  else
    fail build_P "see $R/build_P.log"; grep -E '^error' -A14 $R/build_P.log | head -n 80 >> $LOG
    finish "build failed (a dry-run finding)"
  fi
fi

if done_ build_P && ! done_ gen_P; then
  wait_window
  GEN=$W/programs/P/card_enum_generator
  for m in ids database incremental-attack-map incremental-ability-map; do
    arg=; ref=; case $m in ids) ref=src/card_ids.rs;; database) arg=--database; ref=src/database.rs;; *) arg=--$m;; esac
    ( cd $WT/engine && $G $GEN $arg > $R/gen_$m.out 2>$R/gen_$m.err ); rc=$?
    if [ -n "$ref" ]; then
      if cmp -s <(tr -d ' \t\r\n' < $R/gen_$m.out) <(tr -d ' \t\r\n' < $WT/engine/$ref); then log "gen_P $m: rc=$rc, reproduces $ref (whitespace aside)"
      else log "gen_P $m: rc=$rc, DIFFERS from $ref"; diff -w <(tr -d '\r' < $WT/engine/$ref) <(tr -d '\r' < $R/gen_$m.out) | head -n 20 >> $LOG; fi
    else
      log "gen_P $m: rc=$rc, $(grep -c . $R/gen_$m.out) output lines (expected 0)"; head -n 20 $R/gen_$m.out >> $LOG
    fi
  done
  mark gen_P
fi

if done_ build_P && ! done_ status_P; then
  wait_window
  ( cd $WT/engine && $G $W/programs/P/card_status --json > $R/card_status.json 2>$R/card_status.err ); log "card_status rc=$?"
  python3 -I - $R/card_status.json <<'EOF' | tee -a $LOG
import json, sys, collections
cards = json.load(open(sys.argv[1]))
cards = cards if isinstance(cards, list) else cards.get('cards', cards)
new = [c for c in cards if str(c.get('id', '')).startswith(('B4b ', 'P-B 09'))]
print('card_status: all', len(cards), 'new (B4b, P-B 09x)', len(new))
print('  new by status:', dict(collections.Counter(c.get('status') for c in new)))
names = collections.defaultdict(list)
for c in new:
    if c.get('status') not in ('Complete', 'RulesUnverified'):
        names[(c.get('status'), c.get('name'))].append(c.get('id'))
for (st, nm), ids in sorted(names.items(), key=lambda x: (str(x[0][0]), str(x[0][1]))):
    print(f'  {st}: {nm} {ids}')
EOF
  mark status_P
fi

if done_ build_P && ! done_ suite_P; then
  wait_window; no_cargo
  s=$(date +%s)
  ( cd $WT/engine && RUST_TEST_THREADS=2 $G cargo test --release --features test-utils --locked --no-fail-fast ) > $R/suite_P.log 2>&1
  rc=$?
  res=$(python3 -I - $R/suite_P.log <<'EOF'
import re, sys
t = open(sys.argv[1], errors='replace').read()
p = sum(int(x) for x in re.findall(r'test result: \w+\. (\d+) passed', t))
f = sum(int(x) for x in re.findall(r'(\d+) failed', ' '.join(re.findall(r'test result: [^\n]*', t))))
fails = sorted(set(re.findall(r'^---- (\S+)', t, re.M)))
errs = len(re.findall(r'^error(\[E\d+\])?:', t, re.M))
print(f"passed {p} failed {f} compile_errors {errs} failing {fails[:60]}")
EOF
)
  log "suite_P rc=$rc in $(( $(date +%s) - s )) s: $res"
  mark suite_P
fi

if done_ build_P; then
  if [ ! -e $W/P/.from_$P ]; then
    rm -rf $W/P && mkdir -p $W/P
    git -C $WT -c core.autocrlf=false archive $P engine decks | tar -x -C $W/P
    touch $W/P/.from_$P
  fi
  for n in $REPLAYS; do
    wait_window
    grep -q "^p	$n	" $W/games/summary.tsv 2>/dev/null && continue
    log "replay p $n"
    SCAN_THREADS=8 python3 -u $S/replay3.py p $n >> $R/replays.log 2>&1 || log "replay p $n: exit $?"
  done
  grep -P '^p\t' $W/games/summary.tsv | cut -c1-300 >> $LOG
  mark replays_P
fi
finish "done"
