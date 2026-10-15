#!/usr/bin/env bash
set -euo pipefail
base='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-09_NEW_UPLOADS/20261009_222100000_iOS'
source='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/20261009_222100000_iOS.MP4'
mkdir -p "$base/proof"
if (( $# )); then
  times=("$@")
else
  times=(8 10 15 20 23 25 27 32 34 38 43 47 50 53 57 61 64 67 70 73 77 80 83 86 90 93 96 99 102 106 110 114 118 122 126 130 134 138 142 146 150 154 158 159 160 161 162 163 164 165 166 167 168 169 170 174 180 194)
fi
for t in "${times[@]}"; do
  printf -v label '%03d' "$t"
  ffmpeg -hide_banner -loglevel error -ss "$t" -i "$source" -frames:v 1 -q:v 2 -y "$base/proof/t${label}.jpg"
done
