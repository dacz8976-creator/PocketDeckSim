#!/bin/bash
# 1-fps full-resolution frames for the scorer, named by second (t_SSSS.jpg). usage: frames.sh <recording name in ~/gemini_ladder/src> <out dir>
SRC="/home/dacz8976/gemini_ladder/src/$1"; O="$2"
mkdir -p "$O"
nice -n 19 ffmpeg -v error -i "$SRC" -vf "fps=1,scale=1170:-2" -q:v 3 "$O/f_%04d.jpg" || exit 1
python3 -I - "$O" <<'EOF'
import os, sys
d = sys.argv[1]
for f in sorted(os.listdir(d)):
    if f.startswith('f_'):
        os.rename(f'{d}/{f}', f'{d}/t_{int(f[2:6]) - 1:04d}.jpg')
EOF
echo "frames: $(ls "$O" | wc -l)"
