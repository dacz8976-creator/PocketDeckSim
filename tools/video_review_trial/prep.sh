#!/bin/bash
# Video review trial (Claude v Codex): frames for one game. usage: prep.sh <game dir under ~/video_trial>
# Makes, from source.mp4 (1170x2532 portrait screen recordings):
#   frames/sheets/sheet_NNN.jpg  - overview: 1 frame/s, 234 px wide, 6x3 tiles = 18 s per sheet (labelled by start second)
#   frames/half/t_SSSS.S.jpg     - 2 frames/s at 585 px wide, for following the action
#   frames/full/t_SSSS.jpg       - 1 frame/s at full 1170 px, for reading HP, card text and numbers
set -e
G=/home/dacz8976/video_trial/$1
cd "$G"
mkdir -p frames/sheets frames/half frames/full
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 source.mp4)
echo "duration $dur s"
nice -n 19 ffmpeg -v error -i source.mp4 -vf "fps=1,scale=1170:-2" -q:v 3 frames/full/f_%04d.jpg
nice -n 19 ffmpeg -v error -i source.mp4 -vf "fps=2,scale=585:-2" -q:v 4 frames/half/h_%05d.jpg
nice -n 19 ffmpeg -v error -i source.mp4 -vf "fps=1,scale=234:-2,tile=6x3" -q:v 4 frames/sheets/s_%03d.jpg
# rename to the second each frame shows (ffmpeg's fps filter centres frame n at (n-1)/fps + 0.5/fps)
python3 - "$G/frames" <<'EOF'
import os, sys
d = sys.argv[1]
for f in sorted(os.listdir(f'{d}/full')):
    n = int(f[2:6]); os.rename(f'{d}/full/{f}', f'{d}/full/t_{n-1:04d}.jpg')
for f in sorted(os.listdir(f'{d}/half')):
    n = int(f[2:7]); os.rename(f'{d}/half/{f}', f'{d}/half/t_{(n-1)/2:06.1f}.jpg')
for f in sorted(os.listdir(f'{d}/sheets')):
    n = int(f[2:5]); os.rename(f'{d}/sheets/{f}', f'{d}/sheets/sheet_from_{(n-1)*18:04d}s.jpg')
EOF
echo "full $(ls frames/full | wc -l)  half $(ls frames/half | wc -l)  sheets $(ls frames/sheets | wc -l)  size $(du -sh frames | cut -f1)"
