#!/bin/bash
cd /home/dacz8976/video_trial || exit 1
for f in briefs/*.md run_chunks.sh; do sed -i 's/\r$//' "$f"; done
C3="/mnt/c/Users/dacz8/BattleLogsData/Evidence/DRIVE_LADDER_2026-10-25/1z3BFENvS8a8iOtwXUxkinkeQFnX8r6f7_ScreenRecording_10-24-2026_13-24-53_1.mp4"
setsid tmux new-session -d -s vchunk_h "bash /home/dacz8976/video_trial/run_chunks.sh g3 ch_h claude-haiku-5-5 1.5 '$C3' > /home/dacz8976/video_trial/g3/ch_h.out 2>&1"
setsid tmux new-session -d -s vchunk_s "bash /home/dacz8976/video_trial/run_chunks.sh g3 ch_s claude-sonnet-5-5 3 '$C3' > /home/dacz8976/video_trial/g3/ch_s.out 2>&1"
sleep 5; tmux ls | grep vchunk; ls g3/ch_h/prompts 2>/dev/null | head -3; date -u +%FT%TZ
