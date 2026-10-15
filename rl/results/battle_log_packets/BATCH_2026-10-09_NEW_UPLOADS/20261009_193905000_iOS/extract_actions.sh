#!/bin/bash
set -e
base='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs'
packet="$base/Recording_QA/BATCH_2026-10-09_NEW_UPLOADS/20261009_193905000_iOS"
ffmpeg -threads 2 -hide_banner -i "$base/20261009_193905000_iOS.MP4" -vf "select='(isnan(prev_selected_t)+gte(t-prev_selected_t,1))*((between(t,0,37))+(between(t,39,70))+(between(t,74,106))+(between(t,108,130))+(between(t,133,170))+(gte(t,175)))',showinfo" -fps_mode vfr -q:v 3 "$packet/frames/action_%03d.jpg" 2> "$packet/frame_decode.log"
