#!/bin/bash
# Switch step 2 (113 §2, 151 §3): the official build from the tip 543dad00 with Lane N's own lane_r8.sh (build_R, gen_R,
# status_R), in the same worktree path and a fresh target folder at the same path, so the program sha256s compare with
# Lane N's. suite_R / goldfish_R / replays_R are marked skipped under Q2 (A); if any program sha256 differs from Lane N's,
# the markers are removed and the lane re-run in full (B), as 151 §3 says. Detached; nice 19 inside lane_r8.sh.
set -u
C=543dad0007a345128ec95e9c2698699c8b5493ce
OUT=/home/dacz8976/pincand_work/RR_R8_543dad00; R=$OUT/prep
[ -e /home/dacz8976/credit_work/PAUSE ] && { echo "STOP: PAUSE"; exit 1; }
[ "$(git -C /home/dacz8976/r6v_scratch rev-parse HEAD)" = $C ] || { echo "STOP: scratch HEAD"; exit 1; }
[ -e /home/dacz8976/lane_r8_w ] && { echo "STOP: ~/lane_r8_w exists"; exit 1; }
[ -e /home/dacz8976/lane_r8_target.laneN ] && { echo "STOP: laneN target copy exists"; exit 1; }
[ "$(( $(df -B1 --output=avail /mnt/c | tail -n 1 | tr -dc 0-9) / 1073741824 ))" -ge 15 ] || { echo "STOP: C: under 15 GiB"; exit 1; }
mv /home/dacz8976/lane_r8_target /home/dacz8976/lane_r8_target.laneN
git -C /home/dacz8976/pincand worktree add --detach /home/dacz8976/lane_r8_w $C > /dev/null 2>&1 || { echo "STOP: worktree add"; exit 1; }
mkdir -p $R; echo $C > $R/R_COMMIT
for s in suite_R goldfish_R replays_R; do echo "$(date -u +%FT%TZ) skipped: Q2 (A), coordinator-151 §3 (Lane N's at 48dec4f5 cited; same engine tree)" > $R/$s.done; done
cd /home/dacz8976
setsid nohup bash /home/dacz8976/lane_r8_w/rl/results/r8_catchup_2026-10-29/lane/lane_r8.sh $OUT > /home/dacz8976/relplan/r8/sw/step2_stdout.txt 2>&1 < /dev/null &
echo "started pid $!"
