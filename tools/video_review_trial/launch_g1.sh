#!/bin/bash
cd /home/dacz8976/video_trial || exit 1
C="/mnt/c/Users/dacz8/BattleLogsData/Evidence/DRIVE_LADDER_2026-10-25/1wDuQKnCMNXhyEm3-_qCtZ9gJsi7AZzpA_ScreenRecording_10-24-2026_15-29-43_1.mp4"
ls "$C" | head -20
tmux has-session -t '=vtrial1' 2>/dev/null && { echo "vtrial1 already running"; exit 1; }
setsid tmux new-session -d -s vtrial1 "bash /home/dacz8976/video_trial/run_game.sh g1 '$C' > /home/dacz8976/video_trial/g1/run.out 2>&1"
sleep 2; tmux ls | grep vtrial1; date -u +%FT%TZ
