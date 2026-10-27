#!/bin/bash
# free countTokens probes for one game: sizes at each setting, no charged call
cd /home/dacz8976/gemini_video || exit 1
G=$1; REC="$2"
sed "s/<RECORDING>/$REC/" briefs/FIELD_VIDEO.md > $G/FIELD.md
sed "s/<RECORDING>/$REC/" briefs/REVIEW_VIDEO.md > $G/REVIEW.md
for cfg in "1 LOW" "1 MEDIUM" "2 MEDIUM" "1 HIGH" "2 HIGH"; do
  set -- $cfg
  python3 -I gemini_video.py --video $G/video.mp4 --brief $G/FIELD.md --out $G/dry --fps $1 --resolution $2 --dry 2>&1 | tail -1
done
python3 -I gemini_video.py --video $G/video.mp4 --brief $G/FIELD.md --out $G/dry --fps 1 --dry 2>&1 | tail -1
rm -rf $G/dry
