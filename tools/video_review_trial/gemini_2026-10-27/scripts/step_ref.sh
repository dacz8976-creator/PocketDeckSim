#!/bin/bash
# reference files (the Oct 25-26 trial's checked finals) + full-resolution frames, into the Windows scratchpad for the scorers
S=/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/b816037a-8268-412e-9510-8518f9b17037/scratchpad/gscore
B=claude/video-review-trial-2026-10-26; T=tools/video_review_trial/results
cd /home/dacz8976/credit_work/tools || exit 1
for pair in "g1:g1" "g2:g2/arm_s" "g3:g3/ch_s"; do
  g=${pair%%:*}; d=${pair#*:}
  mkdir -p $S/$g/ref $S/$g/frames
  for f in out_check/REVIEW_FINAL.md out_check/OPPONENT_FINAL.json out_check/CHECK_NOTES.md out_compare/compare.json; do
    git show $B:$T/$d/$f > $S/$g/ref/$(basename $f)
  done
done
for g in g1 g2 g3; do
  src=/home/dacz8976/gemini_video/src/$g.mp4
  [ -f "$src" ] || { echo "$g: no source copy"; continue; }
  nice -n 19 ffmpeg -v error -i "$src" -vf "fps=1,scale=1170:-2" -q:v 3 $S/$g/frames/f_%04d.jpg
  python3 - $S/$g/frames <<'EOF'
import os, sys
d = sys.argv[1]
for f in sorted(os.listdir(d)):
    if f.startswith('f_'):
        n = int(f[2:6]); os.rename(f'{d}/{f}', f'{d}/t_{n-1:04d}.jpg')
EOF
  echo "$g: $(ls $S/$g/frames | wc -l) frames, $(du -sh $S/$g/frames | cut -f1)"; rm -f "$src"
done
ls $S/*/ref
