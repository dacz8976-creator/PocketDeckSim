#!/bin/bash
# The night launcher for exam run 3 (coordinator's GO, Oct 25): waits until 02:00Z (9 PM CDT), then runs MODE=live run_exam3.sh at nice 19.
# Started inside tmux as: tmux new-session -d -s run3live "setsid -w bash /home/dacz8976/arm_run3.sh"
# The Vertex key is read from the LAST `export VERTEX_API_KEY=` line of ~/.bashrc (the first is a placeholder) and never printed.
set -uo pipefail
export KIT_COMMIT=32c7c9cafdcb202bd7ed0f2c488fdc5fd6c16205   # K20's kit commit (dry run dry-20261025T224223Z clean)
WT=/home/dacz8976/exam_034_w
KIT=$WT/rl/results/weekly_review_2026-10-18/exam/run3/run_exam3.sh
L=/home/dacz8976/run3_live_launcher.log
say() { echo "$(date -u +%FT%TZ) $*" >> "$L"; }
say "armed (kit $KIT_COMMIT); waiting for 02:00Z"
while :; do
  [ -e /home/dacz8976/credit_work/PAUSE ] && { say "PAUSE file present: not starting"; exit 1; }
  [ -e /home/dacz8976/run3_DISARM ] && { say "disarmed by /home/dacz8976/run3_DISARM: not starting"; exit 1; }
  HM=$(date -u +%H%M)
  if [ $((10#$HM)) -ge 200 ] && [ $((10#$HM)) -le 1250 ]; then break; fi
  sleep 30
done
[ "$(git -C "$WT" rev-parse HEAD)" = "$KIT_COMMIT" ] && [ -z "$(git -C "$WT" status --porcelain -- rl/results/weekly_review_2026-10-18/exam/run3)" ] \
  || { say "the worktree is not at the kit commit (or has changes in run3/): not starting"; exit 1; }
KEY=$(grep '^export VERTEX_API_KEY=' "$HOME/.bashrc" | tail -n 1 | cut -d= -f2- | sed -e 's/^["'"'"']//' -e 's/["'"'"']$//')
[ ${#KEY} -gt 20 ] || { say "no usable Vertex key line in ~/.bashrc: not starting"; exit 1; }
export VERTEX_API_KEY="$KEY"; unset KEY
say "starting MODE=live run_exam3.sh (nice 19)"
cd /home/dacz8976
MODE=live nice -n 19 bash "$KIT" > /home/dacz8976/run3_live.log 2>&1
say "run_exam3.sh exit $?; see the run folder's run.log and STATUS"
