#!/bin/bash
# K21's night driver (PREREG_RUN3.md addendum 8, K21), started by arm_k21.sh at 02:00Z on the registered nights only:
# Mon Oct 26, Tue Oct 27, Thu Oct 29, Fri Oct 30 (CT) = 2026-10-27, -28, -30, -31 UTC. Never Wednesday night (2026-10-29 UTC, Dual Fusion).
#   night 1: the build (C: >= 15 GB free), the gates (a)-(d) on development positions, the launch line (the binary's sha256) committed and pushed to
#            the exam branch, a note to the coordinator; then kx3's exam rows, seed-major, one position at a time, nice 19, until 12:50Z.
#   later nights: the same binary (sha256 = the launch line's) resumes by (seed, position) until 12:50Z.
#   all 3 seeds complete, or the registered end (13:00Z Oct 31) reached: compare_k21.py (no Gemini call). Results go to the coordinator only.
# Anything the registration does not cover stops it (STATUS STOP and K/STOPPED, which holds every later night) with a note to the coordinator.
#   bash run_k21.sh            (from arm_k21.sh; KIT_COMMIT in $K/KIT_COMMIT)
set -euo pipefail
K=/home/dacz8976/k21_run
KIT=$K/kit
REPO=/home/dacz8976/exam_034_w
J=/home/dacz8976/judge7_w/rl/ai_judge
EXAM_BRANCH=sonnet/exam-2026-10-19
RUN3=rl/results/weekly_review_2026-10-18/exam/run3
SEEDS=25101000001,25101000002,25101000003
LAST_NIGHT=2026-10-31
MAILBOX=/mnt/c/Users/dacz8/Projects/agent-mailbox/messages
BIN=$HOME/k21_pgpos/bin/pg_pos_k21
TODAY=$(date -u +%F)
LOG=$K/night_$TODAY.log
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }
note() {  # $1 short kind, $2 title, $3 body: a mailbox note to the coordinator (information; the laptop session also reports)
  local ts id; ts=$(date -u +%Y%m%dT%H%MZ); id="$ts-laptop-k21$1"
  printf 'id: %s\nfrom: laptop\nto: coordinator\ndate: %s\nkind: report\nre: K21 (unchanged kx3 on exam v2), the night job\n---\n# %s\n\n%s\n' \
    "$id" "$(date -u +%FT%H:%MZ)" "$2" "$3" > "$MAILBOX/coordinator__$id.md" || true
}
fail() {
  log "STOP: $*"; echo STOP > "$K/STATUS_$TODAY"; echo "$TODAY $*" >> "$K/STOPPED"
  note stop "K21 night job STOPPED ($TODAY): no further kx3 row until you decide" "$(printf 'Reason: %s\n\nLog tail:\n```\n%s\n```\nThe stop holds every later night (k21_run/STOPPED). Results, if any, are not in this note.' "$*" "$(tail -n 12 "$LOG")")"
  exit 1
}
trap 'rc=$?; [ -e "$K/STATUS_$TODAY" ] || { log "STOP: unexpected exit $rc (line $LINENO)"; echo STOP > "$K/STATUS_$TODAY"; echo "$TODAY unexpected exit $rc" >> "$K/STOPPED"; note stop "K21 night job STOPPED ($TODAY): unexpected exit $rc" "$(tail -n 12 "$LOG")"; }' EXIT
log "K21 night $TODAY: kit $(cat "$K/KIT_COMMIT" 2>/dev/null || echo none); this script sha256 $(sha256sum "$0" | cut -c1-64)"

# 0. the guards
[ -e "$K/STOPPED" ] && { log "an earlier stop holds ($(tail -n 1 "$K/STOPPED")): nothing runs"; echo HELD > "$K/STATUS_$TODAY"; trap - EXIT; exit 1; }
[ -e "$K/DONE" ] && { log "K21 is done: nothing runs"; echo DONE > "$K/STATUS_$TODAY"; trap - EXIT; exit 0; }
case "$TODAY" in 2026-10-27|2026-10-28|2026-10-30|2026-10-31) ;; *) fail "$TODAY is not a registered night (Oct 27, 28, 30, 31 UTC; never Oct 29)";; esac
HM=$(date -u +%H%M); { [ $((10#$HM)) -ge 200 ] && [ $((10#$HM)) -lt 1250 ]; } || fail "outside the night window (02:00-12:50Z): ${HM}Z"
KIT_COMMIT=$(cat "$K/KIT_COMMIT")
for f in run_k21.sh build_k21.sh gates_k21.py kx3_rows.py compare_k21.py; do
  [ "$(git -C "$REPO" show "$KIT_COMMIT:$RUN3/k21/kit/$f" | sha256sum | cut -c1-64)" = "$(sha256sum "$KIT/$f" | cut -c1-64)" ] || fail "$KIT/$f is not the kit commit's"
done
[ -z "${KX_EXTRA_LISTS:-}" ] || fail "KX_EXTRA_LISTS is set"
[ "$(git -C /home/dacz8976/judge7_w rev-parse HEAD)" = 712593a1b77b203ec23fb15589c158c6bddb2bf2 ] || fail "judge7_w is not the frozen-7 tag"
LIVE=$K/live
python3 -B - "$LIVE" <<'EOF' || fail "the run 3 inputs in $LIVE are not the files run 3 compared with"
import hashlib, json, sys
L = sys.argv[1]
h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
inp = json.load(open(f'{L}/report_primary.json'))['run']['inputs']
assert h(f'{L}/in/positions.json') == inp['positions_sha256']
assert h(f'{L}/report_primary.json') == json.load(open(f'{L}/run_manifest.json'))['files']['report_primary.json']
ids = open(f'{L}/in/ids.txt').read().split()
assert len(ids) == 258 == len(set(ids))
EOF
# Dustin needs the laptop (the PAUSE file): nothing heavy starts until it is gone; still there at 12:50Z, the night is skipped (not a stop),
# except that on the last night the seeds already complete are scored (light)
PAUSED=""
while [ -e "$HOME/credit_work/PAUSE" ]; do
  [ -z "$PAUSED" ] && log "the PAUSE file is present: waiting (nothing starts while it is there)"
  PAUSED=1
  [ $((10#$(date -u +%H%M))) -ge 1250 ] && break
  sleep 60
done
SKIP_ROWS=""
if [ -e "$HOME/credit_work/PAUSE" ]; then
  if [ "$TODAY" = "$LAST_NIGHT" ] && [ -e "$K/launch/COMMIT" ]; then
    log "PAUSE all night: no rows tonight; the registered end: scoring the complete seeds"; SKIP_ROWS=1
  else
    log "PAUSE all night: night skipped"; echo SKIPPED_PAUSE > "$K/STATUS_$TODAY"
    note pause "K21 night $TODAY skipped: the PAUSE file was present all night" "No kx3 row was played tonight. The next registered night resumes."
    exit 0
  fi
fi
[ -n "$PAUSED" ] && [ -z "$SKIP_ROWS" ] && log "PAUSE gone: starting"

# 1. night 1: build, gates, launch line
if [ -n "$SKIP_ROWS" ]; then
  SHA=$(python3 -c "import json; print(json.load(open('$K/launch/LAUNCH_K21.json'))['binary_sha256'])")
elif [ ! -e "$K/launch/LAUNCH_K21.json" ]; then
  FREE=$(df -BG /mnt/c | awk 'NR==2 {gsub("G","",$4); print $4}')
  [ "$FREE" -ge 15 ] || fail "C: has ${FREE} GB free, under the 15 GB build rule"
  pgrep -x cargo > /dev/null && fail "another cargo is running"
  log "build (C: ${FREE} GB free)"
  bash "$KIT/build_k21.sh" > "$K/build.out" 2>&1 || { tail -n 20 "$K/build.out" >> "$LOG"; fail "the build failed (k21_run/build.out, k21_pgpos/build.log)"; }
  SHA=$(sha256sum "$BIN" | cut -c1-64)
  log "$(tail -n 1 "$K/build.out")"
  [ "$(python3 -c "import json; print(json.load(open('$HOME/k21_pgpos/build.json'))['binary_sha256'])")" = "$SHA" ] || fail "build.json does not name the built binary"
  log "gates (a)-(d) on development positions"
  rm -rf "$K/gates"
  python3 -B "$KIT/gates_k21.py" "$K" "$BIN" > "$K/gates.out" 2>&1 || { cat "$K/gates.out" >> "$LOG"; fail "a gate did not pass: $(head -n 1 "$K/gates.out") (k21_run/gates/GATES.json)"; }
  cat "$K/gates.out" | tee -a "$LOG"
  mkdir -p "$K/launch"
  cp "$HOME/k21_pgpos/build.json" "$K/launch/build.json"
  cp "$K/gates/GATES.json" "$K/launch/GATES.json"
  python3 -B - "$K" "$SHA" "$KIT_COMMIT" "$SEEDS" <<'EOF'
import json, sys, datetime
K, sha, kit, seeds = sys.argv[1:5]
g = json.load(open(f'{K}/gates/GATES.json'))
t = [x['seconds'] for x in g['d_timing']]
json.dump({'what': "K21's launch line: the kx3 executable, committed before any kx3 exam row", 'binary_sha256': sha, 'kit_commit': kit, 'seeds': seeds,
           'gates_pass': g['pass'], 'gates_all_pass': g['all_pass'], 'gates_dev_main': g['main'], 'gate_d_kx3_seconds': {'n': len(t), 'mean': round(sum(t) / len(t), 1), 'max': round(max(t), 1)},
           'written_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'kx3_exam_rows_so_far': 0},
          open(f'{K}/launch/LAUNCH_K21.json', 'w'), indent=1)
EOF
  # commit the launch line on the exam branch (plumbing: the worktree is not touched), then push; no row before the push succeeds
  git -C "$REPO" fetch -q origin "$EXAM_BRANCH" || fail "fetch the exam branch"
  TIP=$(git -C "$REPO" rev-parse FETCH_HEAD)
  git -C "$REPO" merge-base --is-ancestor "$KIT_COMMIT" "$TIP" || fail "the exam tip $TIP does not descend from the kit commit"
  git -C "$REPO" diff --quiet "$KIT_COMMIT" "$TIP" -- "$RUN3/k21" "$RUN3/frozen_2026-10-25" "$RUN3/live-20261026T020013Z" || fail "the kit, the freeze or run 3's files changed on the branch since the kit commit"
  T=$(mktemp -d)
  (
    export GIT_INDEX_FILE=$T/index
    git -C "$REPO" read-tree "$TIP"
    for f in LAUNCH_K21.json build.json GATES.json; do
      B=$(git -C "$REPO" hash-object -w "$K/launch/$f")
      git -C "$REPO" update-index --add --cacheinfo 100644,"$B","$RUN3/k21/launch/$f"
    done
    git -C "$REPO" write-tree > "$T/tree"
  ) || fail "building the launch commit"
  C=$(git -C "$REPO" -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com commit-tree "$(cat "$T/tree")" -p "$TIP" \
      -m "Exam run 3: K21 launch line (the kx3 executable's sha256 ${SHA:0:16}, gates (a)-(d) passed on development positions), before any kx3 exam row" \
      -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>") || fail "commit-tree"
  git -C "$REPO" push -q origin "$C:refs/heads/$EXAM_BRANCH" || fail "push of the launch line $C"
  rm -rf "$T"
  echo "$C" > "$K/launch/COMMIT"
  log "launch line committed and pushed: $C (binary $SHA)"
  note launch "K21 launch: gates (a)-(d) passed; binary ${SHA:0:16}; kx3 exam rows starting" "$(printf 'Binary sha256: %s\nLaunch commit on %s: %s\nGates:\n```\n%s\n```\nkx3 rows start now on seeds %s, seed-major, until 12:50Z. No result is in this note.' "$SHA" "$EXAM_BRANCH" "$C" "$(cat "$K/gates.out")" "$SEEDS")"
else
  SHA=$(python3 -c "import json; print(json.load(open('$K/launch/LAUNCH_K21.json'))['binary_sha256'])")
  [ "$(sha256sum "$BIN" | cut -c1-64)" = "$SHA" ] || fail "the binary is not the launch line's ($SHA)"
  git -C "$REPO" fetch -q origin "$EXAM_BRANCH" || fail "fetch the exam branch"
  git -C "$REPO" merge-base --is-ancestor "$(cat "$K/launch/COMMIT")" FETCH_HEAD || fail "the launch commit is not on the exam branch"
  log "resuming with the launch line's binary $SHA"
fi

# 2. kx3's exam rows until 12:50Z (a position in play at 12:58Z is killed and leaves no row)
RC=10
if [ -z "$SKIP_ROWS" ]; then
  set +e
  python3 -B "$KIT/kx3_rows.py" --judge-dir "$J" --bin "$BIN" --bot kx3 --positions "$LIVE/in/positions.json" --decks "$LIVE/in/decks" --ids "$LIVE/in/ids.txt" \
    --seeds "$SEEDS" --out-dir "$K/rows" --stop-at-utc 12:50 --hard-stop-at-utc 12:58 --pause-file "$HOME/credit_work/PAUSE" >> "$K/rows_$TODAY.out" 2>&1
  RC=$?
  set -e
fi
N=$(cat "$K"/rows/rows_*.jsonl 2>/dev/null | grep -c . || true)
log "kx3 rows: exit $RC; $N rows in all ($(for s in ${SEEDS//,/ }; do printf '%s:%s ' "$s" "$(grep -c . "$K/rows/rows_$s.jsonl" 2>/dev/null || echo 0)"; done))"
case $RC in
  0) log "all 3 seeds complete" ;;
  10) if [ "$TODAY" != "$LAST_NIGHT" ]; then echo NIGHT_DONE > "$K/STATUS_$TODAY"; log "night done; resumes next registered night"; exit 0; fi
      log "the registered end: scoring the complete seeds" ;;
  *) fail "kx3_rows.py exit $RC: $(tail -n 2 "$K/rows_$TODAY.out" | tr '\n' ' ')" ;;
esac

# 3. the scoring (no Gemini call)
python3 -B "$KIT/compare_k21.py" --live "$LIVE" --rows "$K/rows" --kx3-sha "$SHA" --out "$K/out" > "$K/compare.out" 2>&1 || fail "compare_k21.py: $(tail -n 1 "$K/compare.out")"
echo DONE > "$K/STATUS_$TODAY"; touch "$K/DONE"
log "K21 scored (k21_run/out/SUMMARY_K21.json); the laptop session reports to the coordinator"
note done "K21 finished: scored, results with the laptop session" "The kx3 rows are complete for the seeds in k21_run/out/SUMMARY_K21.json and the comparison ran (no Gemini call). The laptop session sends you the result; nothing else is told the result."
