#!/bin/sh
set -eu
base='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs'
packet="$base/Recording_QA/BATCH_2026-10-09_NEW_UPLOADS/20261009_194445000_iOS"
for range in '0 20' '140 10' '196 12' '268 4'; do
    set -- $range
    ffmpeg -hide_banner -loglevel error -ss "$1" -t "$2" -i "$base/20261009_194445000_iOS.MP4" -vf 'fps=1,scale=468:1013' "$packet/gap_${1}_%03d.jpg"
done
