#!/bin/bash
C="/mnt/c/Users/dacz8/BattleLogsData/Evidence/DRIVE_LADDER_2026-10-25/1wDuQKnCMNXhyEm3-_qCtZ9gJsi7AZzpA_ScreenRecording_10-24-2026_15-29-43_1.mp4"
find "$C/independent" -maxdepth 2 -type f \( -name '*.md' -o -name '*.json' \) -printf '%P %s\n' | head -20
echo "images in independent: $(find "$C/independent" -type f -name '*.jpg' | wc -l)"
rm -rf /home/dacz8976/video_trial/g1/out_review_haiku /home/dacz8976/video_trial/g1/out_review_sonnet /home/dacz8976/video_trial/g1/trial.log /home/dacz8976/video_trial/g1/run.out /home/dacz8976/video_trial/g1/costs.jsonl
ls /home/dacz8976/video_trial/g1
