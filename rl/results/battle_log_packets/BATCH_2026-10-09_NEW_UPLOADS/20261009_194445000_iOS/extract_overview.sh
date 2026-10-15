#!/bin/sh
set -eu
base='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs'
packet="$base/Recording_QA/BATCH_2026-10-09_NEW_UPLOADS/20261009_194445000_iOS"
ffmpeg -hide_banner -loglevel error -i "$base/20261009_194445000_iOS.MP4" -vf 'fps=1/4,scale=468:1013' "$packet/overview_%03d.jpg"
