#!/bin/bash
set -e
base='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs'
packet="$base/Recording_QA/BATCH_2026-10-09_NEW_UPLOADS/20261009_193905000_iOS"
ffmpeg -hide_banner -loglevel error -i "$base/20261009_193905000_iOS.MP4" -vf 'fps=1/5' -q:v 3 "$packet/frames/coarse_%03d.jpg"
