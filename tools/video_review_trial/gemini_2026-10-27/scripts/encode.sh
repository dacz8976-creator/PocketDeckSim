#!/bin/bash
# Gemini video trial: shrink one game recording to an inline-sized MP4 (under ~19 MB), same timeline, no audio.
# usage: encode.sh <gN> <source path in WSL>   -> ~/gemini_video/<gN>/video.mp4 (the source copy is deleted after)
set -e
G=/home/dacz8976/gemini_video/$1; SRC="$2"
mkdir -p "$G"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC")
# bitrate for ~16 MB: 16e6*8/dur bits/s, capped at 900k
br=$(python3 -c "print(min(900, int(16e6*8/float('$dur')/1000)))")
nice -n 19 ffmpeg -v error -y -i "$SRC" -an -vf "fps=5,scale=540:-2" -c:v libx264 -preset veryfast -b:v ${br}k -maxrate ${br}k -bufsize $((br*2))k -pix_fmt yuv420p "$G/video.mp4"
echo "$1: duration $dur s, target ${br}k, out $(du -m "$G/video.mp4" | cut -f1) MB"
