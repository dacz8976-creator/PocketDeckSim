#!/bin/bash
# usage: step_run.sh gN field|review   (briefs gN/FIELD.md and gN/REVIEW.md already made by step_dry)
cd /home/dacz8976/gemini_video || exit 1
G=$1
case $2 in
  field)  python3 -I gemini_video.py --video $G/video.mp4 --brief $G/FIELD.md  --out $G/out_field  --fps 1 ;;
  review) python3 -I gemini_video.py --video $G/video.mp4 --brief $G/REVIEW.md --out $G/out_review --fps 2 --resolution HIGH ;;
esac
d=$G/out_$2
python3 -c "import json; u=json.load(open('$d/usage.json')); print({k: u.get(k) for k in ('http','seconds','usd','finish_reason','count_tokens')}, {k: u['usage'].get(k) for k in ('promptTokenCount','candidatesTokenCount','thoughtsTokenCount')}); print(u.get('error','')[:600])"
echo "--- answer head"; head -c 1500 $d/response.txt; echo
