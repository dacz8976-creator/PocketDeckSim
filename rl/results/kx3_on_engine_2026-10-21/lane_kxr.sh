#!/bin/bash
# The slow report's re-pin check (rl/results/kx3_on_engine_2026-10-21/SPEC.md), night lane. Night window only (02:00-12:50Z; the
# keeper freezes this process group at 12:55Z and thaws it at 02:00Z). nice 19, ionice -c3; the program's environment scrubbed of
# KX_*, PDL_*, DECKGYM_*, JEV_*, PG_* (as slow_report.py does). In the worktree WT on branch BR (SPEC, configs and rows.json committed
# and pushed before tonight):
#   1. reg: the three registrations (strength_prereg.py; each replays both self-checks on the program), in parallel; each manifest's
#      self-checks must equal the pin texts; then commit and push the registrations (before any game).
#   2. play: replay_b (threads 3) and replay_a (threads 2) in parallel, then replay_c (threads 2).
#   3. compare: compare_dev.py on all three -> COMPARE_DEV.txt (exit status recorded).
set -u
W=/home/dacz8976/pincand_work
K=$W/kxr
WT=/home/dacz8976/kxr_w
BR=laptop/kx3-replay-engine-2026-10-21
D=rl/results/kx3_on_engine_2026-10-21
P=/home/dacz8976/kx_r3/strength
PSHA=7d046b6f9c1dcd9a9a834c2995bad256bc784e804ea08d351878e035cb24d319
SC_KM3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1'
SC_KX3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa'
G="git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com"
LOG=$K/lane_kxr.log
mkdir -p $K $W/pgids
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/lane_kxr.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
mark() { date -u +%FT%TZ > "$K/$1.done"; }
fail() { echo "$(date -u +%FT%TZ) $2" > "$K/$1.FAILED"; log "$1 FAILED: $2"; date -u +%FT%TZ > $K/lane_kxr.end; exit 1; }
in_window() { local m=$((10#$(date -u +%H) * 60 + 10#$(date -u +%M))); [ $m -ge 120 ] && [ $m -lt 770 ]; }
wait_window() { while ! in_window; do sleep 60; done; }
SCRUB=$(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)' | sed 's/^/-u /' | tr '\n' ' ')
N="nice -n 19 ionice -c3"
log "lane_kxr armed (pgid $(cat $W/pgids/lane_kxr.pgid))"
wait_window
log "lane_kxr start"
cd $WT || fail lane "no worktree $WT"
[ "$(git rev-parse --abbrev-ref HEAD)" = $BR ] || fail lane "worktree not on $BR"
[ -z "$(git status --porcelain)" ] || fail lane "worktree not clean"
[ "$(sha256sum $P | cut -d' ' -f1)" = $PSHA ] || fail lane "program sha256 is not $PSHA"
for s in a b c; do [ -s $D/configs/config_replay_$s.json ] || fail lane "no config $s"; done

# 1. registrations
if [ ! -e $K/reg.done ]; then
  for s in a b c; do
    [ -e $D/replay_$s/manifest.json ] && { log "reg $s: already registered"; continue; }
    ( env $SCRUB $N python3 rl/strength/strength_prereg.py --config $D/configs/config_replay_$s.json --out $D/replay_$s --repo . \
        > $K/reg_$s.log 2>&1; echo $? > $K/reg_$s.rc ) &
  done
  wait
  for s in a b c; do
    [ -e $D/replay_$s/manifest.json ] || fail reg "replay_$s not registered (rc $(cat $K/reg_$s.rc 2>/dev/null); $K/reg_$s.log)"
    got=$(python3 -c "import json,sys; m=json.load(open('$D/replay_$s/manifest.json')); print(m['selfcheck']['km3']); print(m['selfcheck']['kx3'])")
    [ "$got" = "$(printf '%s\n%s' "$SC_KM3" "$SC_KX3")" ] || fail reg "replay_$s self-checks differ from the pin texts: $got"
  done
  $G add $D/replay_a $D/replay_b $D/replay_c
  $G commit -q -m "The slow report's re-pin check: the three registrations (before any game; self-checks equal the pin's)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || fail reg "commit failed"
  git push -q origin $BR >> $LOG 2>&1 || log "push of the registrations failed (committed locally; continuing)"
  mark reg; log "reg done: $(git rev-parse --short HEAD)"
fi

# 2. play
run() { env $SCRUB $N $P run --manifest $D/replay_$1/manifest.json --out $D/replay_$1 --threads $2 > $K/run_$1.log 2>&1; echo $? > $K/run_$1.rc; }
if [ ! -e $K/play.done ]; then
  log "play: b (threads 3) and a (threads 2), then c"
  run b 3 &
  pb=$!
  run a 2
  log "play a: rc $(cat $K/run_a.rc)"
  run c 2
  log "play c: rc $(cat $K/run_c.rc)"
  wait $pb
  log "play b: rc $(cat $K/run_b.rc)"
  for s in a b c; do [ "$(cat $K/run_$s.rc)" = 0 ] || fail play "replay_$s run rc $(cat $K/run_$s.rc) ($K/run_$s.log)"; done
  mark play
fi

# 3. compare
python3 $D/compare_dev.py $D/replay_a $D/replay_b $D/replay_c > $K/COMPARE_DEV.txt 2>&1
echo $? > $K/compare.rc
log "compare: rc $(cat $K/compare.rc); $(tail -n 1 $K/COMPARE_DEV.txt)"
mark compare
date -u +%FT%TZ > $K/lane_kxr.end
log "lane_kxr done"
