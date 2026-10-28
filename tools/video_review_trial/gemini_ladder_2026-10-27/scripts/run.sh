#!/bin/bash
# Gemini side-by-side check (Dustin's yes, Oct 27): Gemini reads each new ranked-game recording next to Codex's usual review.
# usage: run.sh [--dry] <recording file name>...   (names as in G:\My Drive\Battle Logs\Reviewed or \Inbox)
# Per game, into ~/gemini_ladder/games/<name without .mp4>/:
#   review_high/  the full review (REVIEW.md, OPPONENT.json, UNCERTAINTIES) at 2 fps, HIGH media resolution  (~$0.10 per game-minute)
#   review_default/  the same brief at the default resolution, the candidate cheap tracker pass            (~$0.04 per game-minute)
# Hard cap: ~/gemini_ladder/ledger.json, $15 for this check (Google credits). A game already done is skipped.
set -u
H=/home/dacz8976/gemini_ladder
DRY=""; [ "${1:-}" = "--dry" ] && { DRY="--dry"; shift; }
CAP=15
for NAME in "$@"; do
  K="${NAME%.mp4}"; G="$H/games/$K"
  if [ -f "$G/review_high/usage.json" ] && [ -f "$G/review_default/usage.json" ]; then echo "$K: done already, skipped"; continue; fi
  SRC=""
  for d in Reviewed Inbox; do [ -f "/mnt/g/My Drive/Battle Logs/$d/$NAME" ] && SRC="/mnt/g/My Drive/Battle Logs/$d/$NAME"; done
  [ -z "$SRC" ] && [ -f "$H/src/$NAME" ] && SRC="$H/src/$NAME"
  [ -z "$SRC" ] && { echo "$K: video not found (copy it to $H/src/ first)"; continue; }
  mkdir -p "$G"
  if [ ! -f "$G/video.mp4" ]; then
    dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC")
    br=$(python3 -c "print(min(900, int(16e6*8/float('$dur')/1000)))")
    nice -n 19 ffmpeg -v error -y -i "$SRC" -an -vf "fps=5,scale=540:-2" -c:v libx264 -preset veryfast -b:v ${br}k -maxrate ${br}k -bufsize $((br*2))k -pix_fmt yuv420p "$G/video.mp4" || { echo "$K: encode failed"; continue; }
    echo "$K: ${dur%.*} s -> $(du -m "$G/video.mp4" | cut -f1) MB"
  fi
  sed "s/<RECORDING>/$NAME/" "$H/briefs/REVIEW_VIDEO.md" > "$G/REVIEW.md"
  python3 -I "$H/gemini_video.py" --video "$G/video.mp4" --brief "$G/REVIEW.md" --out "$G/review_high" --fps 2 --resolution HIGH --ledger "$H/ledger.json" --cap-usd $CAP $DRY | tail -1
  python3 -I "$H/gemini_video.py" --video "$G/video.mp4" --brief "$G/REVIEW.md" --out "$G/review_default" --fps 2 --ledger "$H/ledger.json" --cap-usd $CAP $DRY | tail -1
  [ -z "$DRY" ] && python3 -I "$H/split.py" "$G"
done
if [ -f "$H/ledger.json" ]; then python3 -c "import json; print('ledger \$%.3f of \$15' % json.load(open('$H/ledger.json'))['accrued_usd'])"; fi
exit 0
