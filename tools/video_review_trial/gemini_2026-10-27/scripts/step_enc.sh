#!/bin/bash
# usage: step_enc.sh gN  (src/gN.mp4 already copied in)
cd /home/dacz8976/gemini_video || exit 1
for f in encode.sh gemini_video.py briefs/*.md; do sed -i 's/\r$//' "$f"; done
bash encode.sh "$1" "/home/dacz8976/gemini_video/src/$1.mp4" && rm -f "src/$1.mp4"
ls -la "$1"
