#!/bin/bash
# Re-run only the default-resolution pass for one game whose cheap pass failed (e.g. HTTP 429), then re-split.
# usage: redo_default.sh <recording name without .mp4>
H=/home/dacz8976/gemini_ladder; G="$H/games/$1"
[ -f "$G/video.mp4" ] && [ -f "$G/REVIEW.md" ] || { echo "$1: no encoded video or brief"; exit 1; }
mv "$G/review_default" "$G/review_default_failed_$(date +%H%M%S)"
python3 -I "$H/gemini_video.py" --video "$G/video.mp4" --brief "$G/REVIEW.md" --out "$G/review_default" --fps 2 --ledger "$H/ledger.json" --cap-usd 15 | tail -1
python3 -I "$H/split.py" "$G"
