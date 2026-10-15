#!/bin/bash
set -e
base='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs'
packet="$base/Recording_QA/BATCH_2026-10-09_NEW_UPLOADS/20261009_193905000_iOS"
ffmpeg -threads 2 -hide_banner -i "$base/20261009_193905000_iOS.MP4" -vf "select='(isnan(prev_selected_t)+gte(t-prev_selected_t,0.195))*((between(t,22,24.5))+(between(t,26,29))+(between(t,32,36))+(between(t,40,46))+(between(t,48,58))+(between(t,78,91))+(between(t,108,120))+(between(t,133,147))+(between(t,154,159)))',showinfo" -fps_mode vfr -q:v 3 "$packet/frames/dense_%03d.jpg" 2> "$packet/dense_decode.log"
