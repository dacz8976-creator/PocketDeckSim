#!/bin/bash
cd /home/dacz8976/video_trial || exit 1
for f in briefs/*.md run_arms.sh; do sed -i 's/\r$//' "$f"; done
E=/mnt/c/Users/dacz8/BattleLogsData/Evidence/DRIVE_LADDER_2026-10-25
C2="$E/1RsIddQR8IgV8KA9TM8jDdSDhUOgnEvCS_ScreenRecording_10-24-2026_12-51-31_1.mp4"
C3="$E/1z3BFENvS8a8iOtwXUxkinkeQFnX8r6f7_ScreenRecording_10-24-2026_13-24-53_1.mp4"
ls -d "$C2" "$C3" || exit 1
for g in g2 g3; do [ -d "$g/frames/full" ] && [ "$(ls $g/frames/sheets | wc -l)" -gt 0 ] || { echo "$g frames missing"; exit 1; }; done
setsid tmux new-session -d -s vtrial2 "bash /home/dacz8976/video_trial/run_arms.sh g2 '$C2' > /home/dacz8976/video_trial/g2/run.out 2>&1"
setsid tmux new-session -d -s vtrial3 "bash /home/dacz8976/video_trial/run_arms.sh g3 '$C3' > /home/dacz8976/video_trial/g3/run.out 2>&1"
sleep 2; tmux ls | grep vtrial; date -u +%FT%TZ
