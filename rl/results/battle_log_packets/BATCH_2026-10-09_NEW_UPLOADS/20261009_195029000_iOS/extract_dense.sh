#!/usr/bin/env bash
set -euo pipefail
root='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-09_NEW_UPLOADS/20261009_195029000_iOS'
video='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/20261009_195029000_iOS.MP4'
mkdir -p "$root/dense"
ffmpeg -hide_banner -loglevel error -ss 20 -t 32 -i "$video" -vf 'fps=3,scale=585:-2' -q:v 4 "$root/dense/a_%03d.jpg"
ffmpeg -hide_banner -loglevel error -ss 99 -t 37 -i "$video" -vf 'fps=3,scale=585:-2' -q:v 4 "$root/dense/b_%03d.jpg"
ffmpeg -hide_banner -loglevel error -ss 140 -t 38 -i "$video" -vf 'fps=3,scale=585:-2' -q:v 4 "$root/dense/c_%03d.jpg"
