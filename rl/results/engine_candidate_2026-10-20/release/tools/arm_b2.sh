#!/bin/bash
# arm_b2.sh F_COMMIT: replace the armed lane B (v1, the Oct 20 build's slow-report pin) with lane B v2 (the final candidate),
# and refresh floor2.py for lane A (same defaults; adds the FLOOR2_* options). Lanes wait for 02:00Z; the keeper freezes them.
set -eu
S=/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad
W=/home/dacz8976/pincand_work
R=$W/release
F=$(git -C /home/dacz8976/pincand rev-parse "$1^{commit}")
m=$((10#$(date -u +%H) * 60 + 10#$(date -u +%M))); if [ $m -ge 120 ] && [ $m -lt 770 ]; then echo "inside the night window: arm by hand"; exit 1; fi
mkdir -p $W/hb $R
for f in lane_b2.sh mk_kf.sh replay2.py; do tr -d '\r' < $S/hb/$f > $W/hb/$f; done
tr -d '\r' < $S/pin/floor2.py > $W/floor2.py
bash -n $W/hb/lane_b2.sh; bash -n $W/hb/mk_kf.sh
python3 -c "import ast; [ast.parse(open(p).read()) for p in ('$W/hb/replay2.py', '$W/floor2.py')]; print('python parses')"
grep -c 'tail -[0-9]' $W/hb/lane_b2.sh $W/hb/mk_kf.sh || true
# lane A is armed and frozen: it reads floor2.py only when it starts at 02:00Z
pg=$(cat $W/pgids/lane_b.pgid 2>/dev/null || echo)
if [ -n "$pg" ]; then ps -o pid,stat,comm -g $pg || true; kill -KILL -- -$pg 2>/dev/null || true; rm -f $W/pgids/lane_b.pgid; fi
sleep 1
tmux kill-session -t "=laneB" 2>/dev/null || true
echo "$F" > $R/F_COMMIT
tmux new-session -d -s laneB "setsid -w bash $W/hb/lane_b2.sh"
sleep 45
tmux ls
for l in lane_a lane_b; do pg=$(cat $W/pgids/$l.pgid); echo "$l pgid $pg"; ps -o pid,stat,etime,comm -g $pg; done
tail -n 4 $W/window_keeper.log
cat $R/F_COMMIT; tail -n 3 $R/lane_b.log
