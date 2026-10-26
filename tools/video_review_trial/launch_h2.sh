#!/bin/bash
cd /home/dacz8976/video_trial || exit 1
sed -i 's/\r$//' briefs/BRIEF_SEGMENT.md run_chunks.sh
grep -c 'replace me' briefs/BRIEF_SEGMENT.md
C3="/mnt/c/Users/dacz8/BattleLogsData/Evidence/DRIVE_LADDER_2026-10-25/1z3BFENvS8a8iOtwXUxkinkeQFnX8r6f7_ScreenRecording_10-24-2026_13-24-53_1.mp4"
setsid tmux new-session -d -s vchunk_h2 "bash /home/dacz8976/video_trial/run_chunks.sh g3 ch_h2 claude-haiku-5-5 1.5 '$C3' > /home/dacz8976/video_trial/g3/ch_h2.out 2>&1"
sleep 4; tmux ls | grep vchunk_h2; ls g3/ch_h2/out_segments | head -3
